import os
import webbrowser
import pyperclip
from functools import partial
from threading import Thread, current_thread
from kivy.app import App
from kivy.clock import Clock
from kivy.loader import Loader
from kivy.modules import inspector
from kivy.core.window import Window
from kivy.properties import BooleanProperty, NumericProperty
from kivy.uix.widget import Widget
from kivy.uix.button import Button, ButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.uix.settings import Settings, SettingPath

Loader.num_workers = 8
Loader.max_upload_per_frame = 8
Loader.loading_image = 'img/loading.png'


class SettingDirectory(SettingPath):
    def _validate(self, instance):
        super(SettingDirectory, self)._validate(instance)
        if not os.path.isdir(self.value):
            self.value = os.path.dirname(self.value)


class MainGUI(FloatLayout):
    def __init__(self):
        super(MainGUI, self).__init__()


class Hoverable(Widget):
    hover = BooleanProperty(False)

    def __init__(self, **kwargs):
        Window.bind(mouse_pos=self.on_mouse_pos)
        super(Hoverable, self).__init__(**kwargs)

    def on_mouse_pos(self, *args):
        if self.parent:
            pos = args[1]
            # We use self.parent.to_widget rather than self.to_widget because the result buttons' positions are
            # relative to their parents (this is not a issue for the other hoverable buttons).
            hovered = self.collide_point(*self.parent.to_widget(*pos))
            if self.hover != hovered:
                self.hover = hovered


class HoverableButton(Button, Hoverable):
    pass


class CoverArt(AsyncImage):
    overlay = NumericProperty(0)

    def __init__(self, **kwargs):
        super(CoverArt, self).__init__(**kwargs)
        self.anim_delay = 0.1


class ResultButton(ButtonBehavior, RelativeLayout, Hoverable):
    def __init__(self, result):
        super(ResultButton, self).__init__()
        self.label = Label(text='%s\n%s\n%s' % (result['title'], result['artist'], result['album']), halign='center',
                           font_size='20sp', size_hint=(1, 1), opacity=0)
        self.image = CoverArt(source=result['img'], allow_stretch=True, size_hint=(1, 1))
        self.add_widget(self.image)
        self.add_widget(self.label)
        self.size_hint = (0.25, None)
        self.bind(width=self.set_height)
        self.bind(hover=self.on_hover)

    def set_height(self, *args):
        self.height = self.width
        self.label.text_size = (self.width, None)

    def on_hover(self, *args):
        if self.hover:
            self.label.opacity = 1
            self.image.overlay = 0.6
        else:
            self.label.opacity = 0
            self.image.overlay = 0


class AudioJackGUI(App):
    use_kivy_settings = False

    def __init__(self):
        super(AudioJackGUI, self).__init__()
        self.audiojack = None
        self.gui = None
        self.local_search = None
        self._keyboard = None
        self.current_search_thread = None

        self.error_msg = None
        self.loading_msg = None
        self.results = None
        self.open_file_button = None
        self.cut_file = None
        self.path = None

    def build(self):
        self.gui = MainGUI()
        self.initialize_widgets()
        Clock.schedule_interval(self.check_cb, 1)
        inspector.create_inspector(Window, self.gui)
        return self.gui

    def build_config(self, config):
        config.setdefaults('main', {
            'dl_path': os.getcwd(),
            'auto_cb': 1
        })
        self.path = config.get('main', 'dl_path')

    def build_settings(self, settings):
        settings.register_type('dir', SettingDirectory)
        settings.add_json_panel('Main', self.config, 'settings.json')

    def on_config_change(self, config, section, key, value):
        self.path = config.get('main', 'dl_path')

    def check_cb(self, dt):
        if self.config.getboolean('main', 'auto_cb'):
            cb = pyperclip.paste()
            # Lazy url validation
            if cb.startswith('http'):
                # This is necessary to reset the cursor position in the TextInput box.
                self.gui.ids.url_input.text = ''
                self.gui.ids.url_input.text = cb

    def initialize_widgets(self):
        self.error_msg = self.gui.ids.error_msg.__self__  # Keep a reference to prevent GC when removing from the GUI.
        self.loading_msg = self.gui.ids.loading_msg.__self__
        self.results = self.gui.ids.results.__self__
        self.open_file_button = self.gui.ids.open_file_button.__self__
        self.cut_file = self.gui.ids.cut_file.__self__
        self.hide_error()
        self.hide_loading()
        self.hide_all()
        self.gui.ids.btn_submit.bind(on_release=self.search)
        self.gui.ids.submit_custom.bind(on_release=self.custom)
        self.gui.ids.url_input.bind(on_text_validate=self.search, focus=self.auto_hide_error)
        self.gui.ids.results_grid.bind(minimum_height=self.gui.ids.results_grid.setter('height'))

    def search(self, *args):
        self.hide_error()
        self.hide_all()
        url = self.gui.ids.url_input.text
        self.loading()
        # call self._search in new thread
        self.current_search_thread = Thread(target=self._search, args=(url,))
        self.current_search_thread.start()

    def _search(self, url):
        self.audiojack.search(url)

    def select(self, index, *args):
        print(self.path)
        self.hide_all()
        self.hide_error()
        self.loading()
        self.current_search_thread = Thread(target=self._select, args=(index,))
        self.current_search_thread.start()
        return True

    def _select(self, index):
        self.local_search.select(index, path=self.path)
        self.notify()

    def custom(self, *args):
        self.hide_all()
        self.hide_error()
        self.loading()
        self.current_search_thread = Thread(target=self._custom)
        self.current_search_thread.start()

    def _custom(self):
        self.local_search.custom(self.gui.ids.custom_title.text, self.gui.ids.custom_artist.text,
                                 self.gui.ids.custom_album.text, path=self.path)
        self.notify()

    def hide_all(self):
        self.hide_results()
        self.hide_file()
        self.hide_cut_file()

    def hide_results(self, *args):
        if self.results.parent:
            self.results.parent.remove_widget(self.results)
        self.gui.ids.results_grid.clear_widgets()

    def handle_results(self, *args):
        if len(self.local_search.results) == 0:
            self.gui.ids.results_label.text = 'No results found.'
        else:
            self.gui.ids.results_label.text = '%d results found.' % len(self.local_search.results)
            for i, result in enumerate(self.local_search.results):
                result_btn = ResultButton(result)
                result_btn.bind(on_release=partial(self.select, i))
                self.gui.ids.results_grid.add_widget(result_btn)
        self.show_results()

    def show_results(self):
        if not self.results.parent:
            self.gui.ids.main_layout.add_widget(self.results)

    def handle_selection(self, *args):
        print(self.local_search.selection)

    def hide_file(self):
        if self.open_file_button.parent:
            self.open_file_button.parent.remove_widget(self.open_file_button)

    def hide_cut_file(self):
        if self.cut_file.parent:
            self.cut_file.parent.remove_widget(self.cut_file)

    def handle_file(self, *args):
        self.open_file_button.text = 'Open %s' % self.local_search.file
        self.open_file_button.bind(on_release=self.open_file)
        self.gui.ids.cut_file_btn.bind(on_release=self.cut)
        if not self.open_file_button.parent:
            self.gui.ids.main_layout.add_widget(self.open_file_button)
        if not self.cut_file.parent:
            self.gui.ids.main_layout.add_widget(self.cut_file)

    def open_file(self, *args):
        webbrowser.open(self.local_search.file)

    def cut(self, *args):
        start = self.gui.ids.start_time.text
        start = int(start) if start.isdigit() else 0
        end = self.gui.ids.end_time.text
        end = int(end) if end.isdigit() else None
        self.local_search.cut_file(start, end)

    def hide_loading(self, *args):
        if self.loading_msg.parent:
            self.loading_msg.parent.remove_widget(self.loading_msg)

    def loading(self):
        if not self.loading_msg.parent:
            self.gui.ids.main_layout.add_widget(self.loading_msg)

    def hide_error(self, *args):
        if self.error_msg.parent:
            self.error_msg.parent.remove_widget(self.error_msg)

    def auto_hide_error(self, *args):
        if self.gui.ids.url_input.focus:
            self.hide_error()

    def handle_error(self, error, *args):
        # TODO: More descriptive error messages
        self.hide_all()
        if not self.error_msg.parent:
            self.gui.ids.main_layout.add_widget(self.error_msg)
        self.error_msg.text = 'An unknown error occurred.'

    def notify(self):
        if current_thread() == self.current_search_thread:
            print('Notified current thread')
            self.hide_loading()
            self.local_search = self.audiojack.last_search
            if self.local_search:
                if self.local_search.error != 0:
                    # GUI changes must be done in the main thread.
                    Clock.schedule_once(partial(self.handle_error, self.local_search.error))
                else:
                    if self.local_search.file:
                        Clock.schedule_once(self.handle_file)
                    elif self.local_search.selection:
                        Clock.schedule_once(self.handle_selection)
                    elif self.local_search.results is not None:
                        # An empty array by itself will evaluate to false so we check if it equals None instead.
                        Clock.schedule_once(self.handle_results)
        else:
            print('Notified outdated thread')
