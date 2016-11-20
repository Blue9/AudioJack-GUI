import Queue
from io import BytesIO
from Tkinter import *
from threading import Thread
from ttk import Progressbar, Scrollbar # Tkinter's default scrollbar is not very pretty
from PIL import Image, ImageTk
import audiojack
from datetime import datetime

class AudioJackGUI(object):
    def __init__(self, master):
        self.root = master
        self.searching = False
        self.can_download = True
        audiojack.set_useragent('AudioJack', '1.0')
        self.frame = ScrollableFrame(self.root)
        self.frame.setconfig(bg='#0D47A1', width=1280, height=720)
        self.frame.pack(side=TOP, fill=BOTH, expand=1)
        self.label = Label(self.frame.mainframe, text='AudioJack', fg='#ffffff', bg=self.frame.mainframe['background'], font=('Segoe UI', 48))
        self.label.pack()
        self.url_entry = Entry(self.frame.mainframe, width=48, font=('Segoe UI', 20), bg='#1565C0', bd=2, highlightthickness=1, highlightcolor='#1565C0', highlightbackground='#0D47A1', fg='#ffffff', insertbackground='#ffffff', relief=FLAT, insertwidth=1)
        self.url_entry.pack()
        self.submit_button = Button(self.frame.mainframe, width=60, font=('Segoe UI', 16), text='Go!', bd=0, bg='#1E88E5', fg='#ffffff', activebackground='#2196F3', activeforeground='#ffffff', relief=SUNKEN, cursor='hand2', command=self.submit)
        self.submit_button.pack()

        self.search_progress = Progressbar(self.frame.mainframe, orient='horizontal', length=720, maximum=100 ,mode='indeterminate')

        self.error_info = Label(self.frame.mainframe, fg='#ff0000', bg=self.frame.mainframe['background'])

        # Use pack_forget on this to reset the view
        self.contents = Frame(self.frame.mainframe, bg=self.frame.mainframe['background'])

        # Contains results and custom tag options
        self.select_frame = Frame(self.contents, bg=self.frame.mainframe['background'])
        self.select_frame.pack()

        #Search results
        self.results_label = Label(self.select_frame, text='Results:', fg='#ffffff', bg=self.frame.mainframe['background'])
        self.results_frame = Frame(self.select_frame, bg=self.frame.mainframe['background'])
        self.results_label.pack()
        self.results_frame.pack()

        # Downloads
        self.file_label = Label(self.contents, fg='#ffffff', bg=self.frame.mainframe['background'])

    def submit(self):
        self.searching = True

        self.error_info.pack_forget()
        self.error_info.config(text='')
        self.contents.pack_forget()
        self.reset_results_frame()
        self.file_label.config(text='')

        self.results_queue = Queue.Queue()
        t = Thread(target=self.search)
        t.daemon = True
        t.start()
        self.submit_button.pack_forget()
        self.search_progress.pack()
        self.search_progress.start(10)
        self.root.after(100, self.handle_results)

    def search(self):
        url = self.url_entry.get()
        try:
            self.results_queue.put(audiojack.get_results(url))
        except Exception as e:
            self.results_queue.put([])

    def handle_results(self):
        try:
            results = self.results_queue.get(0)
            self.reset_results_frame()
            self.search_progress.pack_forget()
            self.submit_button.pack()
            if results == []:
                self.error_info.config(text='No results found.')
                self.error_info.pack()
            else:
                for i, entry in enumerate(results):
                    self.get_result_box(entry).grid(row=i / 4, column=i % 4)
                self.contents.pack()
                self.select_frame.pack()
        except Queue.Empty:
            self.root.after(100, self.handle_results)

    def reset_results_frame(self):
        for result in self.results_frame.winfo_children():
            result.destroy()

    def get_result_box(self, entry):
        try:
            text ='%s\n%s\n%s' % (entry['title'], entry['artist'], entry['album'])
            raw_image = Image.open(BytesIO(entry['img'].decode('base64')))
            side = self.frame.mainframe.winfo_reqwidth() / 4
            image_data = raw_image.resize((side, side), Image.ANTIALIAS)
            image = ImageTk.PhotoImage(image=image_data)
            frame = Frame(self.results_frame)
            button = Button(frame, fg='#ffffff', text=text, image=image, compound=CENTER, bg=self.frame.mainframe['background'], command=lambda: self.select(entry))
            button.image = image
            button.pack(fill=BOTH, expand=1)
            return frame
        except Exception as e:
            print e
            print type(e)

    def select(self, entry):
        if self.can_download:
            self.can_download = False
            self.searching = False
            self.download_queue = Queue.Queue()
            t = Thread(target=lambda: self.get_select(entry))
            t.daemon = True
            t.start()
            self.root.after(100, self.handle_download)

    def get_select(self, entry):
        try:
            self.download_queue.put(audiojack.select(entry))
        except Exception:
            self.download_queue.put('')

    def handle_download(self):
            try:
                file = self.download_queue.get(0)
                self.can_download = True
                if not self.searching:
                    label_text = 'Downloaded %s' % file
                    self.select_frame.pack_forget()
                    self.file_label.config(text=label_text)
                    self.file_label.pack()
                    self.contents.pack()
            except Queue.Empty:
                self.root.after(100, self.handle_download)

class ScrollableFrame(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        scrollbar = Scrollbar(self, orient=VERTICAL)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.canvas = Canvas(self, bd=0, highlightthickness=0, yscrollcommand=scrollbar.set)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=1)
        scrollbar.config(command=self.canvas.yview)
        
        self.mainframe = Frame(self.canvas)
        self.mainframe_id = self.canvas.create_window((0, 0), window=self.mainframe, anchor=NW)
        self.mainframe.bind('<Configure>', self.config_mainframe)
        self.canvas.bind('<Configure>', self.config_canvas)

    def config_mainframe(self, event):
        size = (0, 0, self.mainframe.winfo_reqwidth(), self.mainframe.winfo_reqheight())
        self.canvas.config(scrollregion=size)
    
    def config_canvas(self, event):
        if self.mainframe.winfo_width() != self.canvas.winfo_width():
            self.canvas.itemconfig(self.mainframe_id, width=self.canvas.winfo_width())

    def setconfig(self, bg=None, width=None, height=None):
        self.mainframe.config(bg=bg, width=width, height=height)
        self.canvas.config(bg=bg, width=width, height=height)

if __name__ == '__main__':
    root = Tk()
    app = AudioJackGUI(root)
    root.mainloop()