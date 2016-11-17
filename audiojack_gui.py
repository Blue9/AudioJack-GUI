import Queue
import os
import tkFileDialog
import ttk
import webbrowser
from Tkinter import *
from cStringIO import StringIO
from functools import partial
from threading import Thread

import pyperclip
import validators
from PIL import Image, ImageTk
from musicbrainzngs.musicbrainz import NetworkError
from validators import ValidationFailure
from youtube_dl.utils import ExtractorError, DownloadError

import audiojack

audiojack.set_useragent('AudioJack-GUI', '0.4.0')


class AudioJackGUI(object):
    def __init__(self, master):
        self.stop_cb_check = True

        self.master = master
        self.font = ('Segoe UI', 10)
        
        self.master.minsize(width=800, height=600)
        
        self.canvas = Canvas(self.master, bd=0, highlightthickness=0)
        self.mainframe = ttk.Frame(self.canvas)
        self.scrollbar = Scrollbar(self.master, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.canvas.create_window((0, 0), window=self.mainframe, anchor=N, tags='self.mainframe')
        self.mainframe.bind('<Configure>', self.configure)
        self.mainframe.pack(side=TOP, fill=X)
        self.canvas.pack(side=TOP, fill=BOTH, expand=1)

        self.footer = Frame(self.master, bg='#ddd')
        self.credits = Label(self.footer, text='AudioJack v0.4.0', font=('Segoe UI', 14),
                             bg='#ddd')  # Use Tkinter label because ttk does not make it easy to change colors.
        self.support_link = Label(self.footer, text='Support', font=('Segoe UI', 14), fg='#167ac6', bg='#ddd')
        self.support_link.bind('<Enter>', self.enter_link)
        self.support_link.bind('<Button-1>', self.open_url)
        self.support_link.bind('<Leave>', self.leave_link)
        self.credits.pack(side=LEFT)
        self.support_link.pack(side=RIGHT)
        self.footer.pack(side=BOTTOM, fill=X)

        self.canvas.bind_all('<MouseWheel>', self.scroll)

        self.title = ttk.Label(self.mainframe, text='AudioJack', font=('Segoe UI', 24))
        self.title.pack()

        self.url = ttk.Label(self.mainframe, text='Enter a YouTube or SoundCloud URL below.', font=self.font)
        self.url.pack()

        self.url_input = Text(self.mainframe, width=40, height=1, font=self.font, wrap=NONE)
        self.url_input.bind("<Tab>", focus_next_window)
        self.url_input.bind('<Return>', self.search)
        self.url_input.bind('<Control-Key-a>', self.select_all)
        self.url_input.bind('<Control-Key-A>', self.select_all)
        self.url_input.pack()

        self.submit = ttk.Button(self.mainframe, text='Go!', command=self.search)
        self.submit.pack()

        self.new_cb = ""
        self.old_cb = pyperclip.paste()
        self.stop_cb_check = False

    def configure(self, e):
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def scroll(self, e):
        # TODO: Fix scrolling
        if self.mainframe.winfo_height() > self.master.winfo_height():
            self.canvas.yview_scroll(-1*(e.delta/30), 'units')
    
    def enter_link(self, e):
        self.support_link.configure(cursor='hand2', font=('Segoe UI', 14, 'underline'))

    def open_url(self, e):
        webbrowser.open('http://blue9.github.io/AudioJack-GUI/', autoraise=True)

    def leave_link(self, e):
        self.support_link.configure(cursor='arrow', font=('Segoe UI', 14))

    def select_all(self, e):
        self.url_input.tag_add(SEL, '1.0', END)
        self.url_input.mark_set(INSERT, '1.0')
        self.url_input.see(INSERT)
        return 'break'

    def disable_search(self):
        self.url_input.config(state=DISABLED)
        self.submit.config(state=DISABLED)
        self.url_input.unbind('<Return>')

    def enable_search(self):
        self.url_input.config(state=NORMAL)
        self.submit.config(state=NORMAL)
        self.url_input.bind('<Return>', self.search)

    def cancel_search(self):
        self.cancel.configure(text='Please wait...')
        global run
        run = False

    def get_results(self, input):
        try:
            results = audiojack.get_results(input)[:8]
            images = []
            for i, result in enumerate(results):
                if run:
                    image_data = Image.open(StringIO(results[i]['img'].decode('base64')))
                    image_data = image_data.resize((200, 200), Image.ANTIALIAS)
                    images.append(ImageTk.PhotoImage(image=image_data))
                else:
                    break
            if run:
                self.q.put([results, images])
            else:
                self.q.put(0)
        except (ExtractorError, DownloadError):  # If the URL is invalid,
            self.q.put(-1)  # put -1 into the queue to indicate that the URL is invalid.
        except NetworkError:
            self.q.put(-2)

    def search(self, event=None):
        global run
        run = True
        input = self.url_input.get(0.0, END).replace('\n', '').replace(' ', '').replace('\t', '')
        self.reset()
        self.q = Queue.Queue()
        t = Thread(target=self.get_results, args=[input])
        t.daemon = True
        t.start()
        self.disable_search()
        self.search_progress = ttk.Progressbar(self.mainframe, length=200, mode='indeterminate')
        self.search_progress.pack()
        self.search_progress.start(20)
        self.cancel = ttk.Button(self.mainframe, text='Cancel', command=self.cancel_search)
        self.cancel.pack()
        self.master.after(100, self.add_results)

    def add_results(self):
        try:
            self.results_images = self.q.get(0)
            self.search_progress.pack_forget()
            self.search_progress.destroy()
            self.cancel.pack_forget()
            self.cancel.destroy()
            if self.results_images == 0:
                self.reset()
            elif self.results_images == -1:  # If the URL is invalid
                self.error = ttk.Label(self.mainframe, text='Error: Invalid URL', font=self.font, foreground='#ff0000')
                self.error.pack()  # Create an error message
                self.enable_search()  # Enable the search option again
            elif self.results_images == -2:
                self.error = ttk.Label(self.mainframe, text='Error: Network error', font=self.font,
                                       foreground='#ff0000')
                self.error.pack()  # Create an error message
                self.enable_search()  # Enable the search option again
            else:
                self.enable_search()
                self.results = self.results_images[0]
                self.images = self.results_images[1]
                self.results_frame = ttk.Frame(self.mainframe)
                self.results_label = ttk.Label(self.mainframe, text='Results:', font=self.font)
                self.results_label.pack()
                for i, result in enumerate(self.results):
                    text = '%s\n%s\n%s' % (result['title'], result['artist'], result['album'])
                    self.result = ttk.Button(self.results_frame, text=text, image=self.images[i], compound=TOP, command=partial(self.download, result))
                    self.result.grid(column=i%4, row=i/4)
                self.results_frame.pack()
                self.create_custom_frame(result['url'])
        except Queue.Empty:
            self.master.after(100, self.add_results)

    def create_custom_frame(self, url):
        self.custom_frame = ttk.Frame(self.mainframe)
        self.custom_title = ttk.Label(self.custom_frame, text='Custom tags:')
        self.artist_label = ttk.Label(self.custom_frame, text='Artist: ')
        self.artist_input = Text(self.custom_frame, width=20, height=1, font=self.font)
        self.artist_input.bind("<Tab>", focus_next_window)
        self.title_label = ttk.Label(self.custom_frame, text='Title: ')
        self.title_input = Text(self.custom_frame, width=20, height=1, font=self.font)
        self.title_input.bind("<Tab>", focus_next_window)
        self.album_label = ttk.Label(self.custom_frame, text='Album: ')
        self.album_input = Text(self.custom_frame, width=20, height=1, font=self.font)
        self.album_input.bind("<Tab>", focus_next_window)
        self.cover_art = ttk.Button(self.custom_frame, text='Browse for cover art', command=self.cover_art_browse)
        self.cover_art_path = Entry(self.custom_frame, width=20, font=self.font)
        self.custom_submit = ttk.Button(self.custom_frame, text='Download using custom tags', command=partial(self.custom, url))
        self.custom_title.grid(row=0, columnspan=2)
        self.artist_label.grid(column=0, row=1)
        self.artist_input.grid(column=1, row=1)
        self.title_label.grid(column=0, row=2)
        self.title_input.grid(column=1, row=2)
        self.album_label.grid(column=0, row=3)
        self.album_input.grid(column=1, row=3)
        self.cover_art.grid(column=0, row=4)
        self.cover_art_path.grid(column=1, row=4)
        self.custom_submit.grid(row=5, columnspan=2, sticky=EW, pady=10)
        self.custom_frame.pack(pady=10)

    def cover_art_browse(self):
        image = tkFileDialog.askopenfilename(initialdir=os.path.expanduser('~'), parent=root,
                                             filetypes=[('JPEG files', '*.jpg')])
        self.cover_art_path.delete(0, END)
        self.cover_art_path.insert(0, image)
    
    def get_file(self, entry, download_queue):
        try:
            file = audiojack.select(entry)
            download_queue.put(file)
        except DownloadError as e:
            if 'ffprobe' in str(e) or 'ffmpeg' in str(e):  # Checks if the error is cause by ffmpeg not being installed
                file = '%s/Downloads/%s.temp' % (os.path.expanduser('~'), audiojack.title)  # Delete temp file
                try:
                    os.remove(file)
                except Exception:
                    pass
                download_queue.put(0)

    def download(self, entry):
        self.reset()
        self.download_queue = Queue.Queue()
        dl_t = Thread(target=self.get_file, args=[entry, self.download_queue])
        dl_t.daemon = True
        dl_t.start()
        self.disable_search()
        self.download_progress = ttk.Progressbar(self.mainframe, length=200, mode='indeterminate')
        self.download_progress.pack()
        self.download_progress.start(20)
        self.master.after(100, self.add_file)

    def add_file(self):
        try:
            result = self.download_queue.get(0)
            if result == 0:
                self.error = ttk.Label(self.mainframe, text='Error: ffmpeg is not installed.', font=self.font,
                                       foreground='#ff0000')
                self.error.pack()
            else:
                self.file = result.replace('/', '\\')
                text = 'Open %s' % self.file
                self.file_button = ttk.Button(self.mainframe, text=text, command=partial(self.open_file, self.file))

                self.file_button.pack()
                self.start_time_label = ttk.Label(self.mainframe, text='Start time: ')
                self.start_time_label.pack()
                self.start_time_input = Text(self.mainframe, width=20, height=1, font=self.font)
                self.start_time_input.bind("<Tab>", focus_next_window)
                self.start_time_input.pack()
                self.end_time_label = ttk.Label(self.mainframe, text='End time: ')
                self.end_time_label.pack()
                self.end_time_input = Text(self.mainframe, width=20, height=1, font=self.font)
                self.end_time_input.bind("<Tab>", focus_next_window)
                self.end_time_input.pack()
                self.cut_button = ttk.Button(self.mainframe, text="Cut File", command=self.cut)
                self.cut_button.pack()

            self.enable_search()
            self.download_progress.pack_forget()
            self.download_progress.destroy()
            self.results_label.pack_forget()
            self.results_label.destroy()
            self.results_frame.pack_forget()
            self.results_frame.destroy()
        except Queue.Empty:
            self.master.after(100, self.add_file)

    def custom(self, url):
        entry = {
            'artist': self.artist_input.get(0.0, END).replace('\n', ''),
            'title': self.title_input.get(0.0, END).replace('\n', ''),
            'album': self.album_input.get(0.0, END).replace('\n', ''),
            'url': url
        }
        try:
            with open(self.cover_art_path.get().replace('\n', ''), 'rb') as file:
                entry['img'] = file.read().encode('base64')
        except IOError:
            print 'File not found'
        self.reset()
        file = audiojack.select(entry).replace('/', '\\')
        text = 'Open %s' % file
        self.file = ttk.Button(self.mainframe, text=text, command=partial(self.open_file, file))
        self.file.pack()

    def open_file(self, file):
        os.startfile(file)

    def cut(self):
        """ Cut the mp3 file """
        self.file_button.config(state=DISABLED)
        self.cut_button.config(state=DISABLED)
        start_time = self.start_time_input.get(0.0, END).replace('\n', '')
        end_time = self.end_time_input.get(0.0, END).replace('\n', '')
        self.master.update_idletasks()
        audiojack.cut_file(self.file, start_time, end_time)
        self.file_button.config(state=NORMAL)
        self.cut_button.config(state=NORMAL)

    def reset(self):
        self.url_input.delete(0.0, END)
        self.url_input.config(state=NORMAL)
        self.submit.config(state=NORMAL)

        try:
            self.error.pack_forget()
            self.error.destroy()
        except Exception:
            pass

        try:
            self.cancel.pack_forget()
            self.cancel.destroy()
        except Exception:
            pass

        try:
            self.results_label.pack_forget()
            self.results_label.destroy()
        except Exception:
            pass

        try:
            self.results_frame.pack_forget()
            self.results_frame.destroy()
        except Exception:
            pass

        try:
            self.custom_frame.pack_forget()
            self.custom_frame.destroy()
        except Exception:
            pass

        try:
            self.file.pack_forget()
            self.file.destroy()
        except Exception:
            pass

        try:
            self.file_button.pack_forget()
            self.file_button.destroy()
        except Exception:
            pass

        try:
            self.start_time_label.pack_forget()
            self.start_time_label.destroy()
        except Exception:
            pass

        try:
            self.start_time_input.pack_forget()
            self.start_time_input.destroy()
        except Exception:
            pass

        try:
            self.end_time_label.pack_forget()
            self.end_time_label.destroy()
        except Exception:
            pass

        try:
            self.end_time_input.pack_forget()
            self.end_time_input.destroy()
        except Exception:
            pass

        try:
            self.cut_button.pack_forget()
            self.cut_button.destroy()
        except Exception:
            pass

def focus_next_window(event):
    """ Focus next element """
    event.widget.tk_focusNext().focus()
    return("break")


root = Tk()
root.title('AudioJack-GUI v0.4.0')
root.iconbitmap('AudioJack Icon.ico')
app = AudioJackGUI(root)


def is_url(strg):
    try:
        return validators.url(strg)
    except ValidationFailure:
        return False


def check_cb():
    if not app.stop_cb_check:
        app.new_cb = pyperclip.paste()
        if not (app.new_cb is app.old_cb):
            app.old_cb = app.new_cb
            if is_url(app.old_cb):
                app.url_input.delete(0.0, END)
                app.url_input.insert(INSERT, app.old_cb)
    root.after(1000, check_cb)


root.after(5000, check_cb)
root.mainloop()
