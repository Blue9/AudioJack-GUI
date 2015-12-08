import os
from functools import partial

from threading import Thread
import Queue

from Tkinter import *
import ttk
from PIL import Image, ImageTk
from cStringIO import StringIO
import audiojack

audiojack.set_useragent('AudioJack-GUI v2', '0.1')

class AudioJackGUI_v2(object):
    def __init__(self, master):
        self.master = master
        self.font = ('Segoe UI', 10)
        
        self.master.minsize(width=1280, height=720)
        self.mainframe = ttk.Frame(self.master)
        self.mainframe.pack()
        
        self.title = ttk.Label(self.mainframe, text='AudioJack', font=('Segoe UI Light', 24))
        self.title.pack()
        
        self.url = ttk.Label(self.mainframe, text='Enter a YouTube or SoundCloud URL below.', font=self.font)
        self.url.pack()
        
        self.url_input = Text(self.mainframe, width=40, height=1, font=self.font, wrap=NONE)
        self.url_input.bind('<Return>', self.search)
        self.url_input.pack()
        
        self.submit = ttk.Button(self.mainframe, text='Go!', command=self.search)
        self.submit.pack()
    
    def reset(self):
        self.url_input.delete(0.0, END)
        
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
    
    def get_results(self, input):
        results = audiojack.get_results(input)
        images = []
        for i, result in enumerate(results[:8]):
            image_data = Image.open(StringIO(audiojack.get_cover_art_as_data(results[i][3]).decode('base64')))
            image_data = image_data.resize((200, 200), Image.ANTIALIAS)
            images.append(ImageTk.PhotoImage(image=image_data))
        self.q.put([results, images])
    
    def search(self, event=None):
        input = self.url_input.get(0.0, END).replace('\n', '')
        self.reset()
        self.q = Queue.Queue()
        t = Thread(target=self.get_results, args=[input])
        t.start()
        self.master.after(100, self.add_results)
    
    def add_results(self):
        try:
            self.results_images = self.q.get(0)
            self.results = self.results_images[0]
            self.images = self.results_images[1]
            self.results_frame = ttk.Frame(self.mainframe)
            self.results_label = ttk.Label(self.mainframe, text='Results:', font=self.font)
            self.results_label.pack()
            for i, result in enumerate(self.results[:8]):
                text = '%s\n%s\n%s' % (result[0], result[1], result[2])
                self.result = ttk.Button(self.results_frame, text=text, image=self.images[i], compound=TOP, command=partial(self.download, i))
                self.result.grid(column=i%4, row=i/4)
            self.results_frame.pack()
            self.create_custom_frame()
        except Queue.Empty:
            self.master.after(100, self.add_results)
    
    def create_custom_frame(self):
        self.custom_frame = ttk.Frame(self.mainframe)
        self.custom_title = ttk.Label(self.custom_frame, text='Custom tags:')
        self.artist_label = ttk.Label(self.custom_frame, text='Artist: ')
        self.artist_input = Text(self.custom_frame, width=20, height=1, font=self.font)
        self.title_label = ttk.Label(self.custom_frame, text='Title: ')
        self.title_input = Text(self.custom_frame, width=20, height=1, font=self.font)
        self.album_label = ttk.Label(self.custom_frame, text='Album: ')
        self.album_input = Text(self.custom_frame, width=20, height=1, font=self.font)
        self.custom_submit = ttk.Button(self.custom_frame, text='Download using custom tags', command=self.custom)
        self.custom_title.grid(row=0, columnspan=2)
        self.artist_label.grid(column=0, row=1)
        self.artist_input.grid(column=1, row=1)
        self.title_label.grid(column=0, row=2)
        self.title_input.grid(column=1, row=2)
        self.album_label.grid(column=0, row=3)
        self.album_input.grid(column=1, row=3)
        self.custom_submit.grid(row=4, columnspan=2, sticky=EW, pady=10)
        self.custom_frame.pack(pady=10)
    
    def get_file(self, index, download_queue):
        file = audiojack.select(index)
        download_queue.put(file)
    
    def download(self, index):
        self.reset()
        self.download_queue = Queue.Queue()
        t = Thread(target=self.get_file, args=[index, self.download_queue])
        t.start()
        self.master.after(100, self.add_file)
    
    def add_file(self):
        try:
            self.file = self.download_queue.get(0)
            text = 'Open %s' % self.file
            self.file_button = ttk.Button(self.mainframe, text=text, command=partial(self.open_file, self.file))
            self.results_label.pack_forget()
            self.results_label.destroy()
            self.results_frame.pack_forget()
            self.results_frame.destroy()
            self.file_button.pack()
        except Queue.Empty:
            self.master.after(100, self.add_file)
    
    def custom(self):
        artist = self.artist_input.get(0.0, END).replace('\n', '')
        title = self.title_input.get(0.0, END).replace('\n', '')
        album = self.album_input.get(0.0, END).replace('\n', '')
        self.reset()
        file = audiojack.custom(artist, title, album)
        text = 'Open %s' % file
        self.file = ttk.Button(self.mainframe, text=text, command=partial(self.open_file, file))
        self.file.pack()
    
    def open_file(self, file):
        os.startfile(file)

root = Tk()
root.title('AudioJack-GUI v2')
app = AudioJackGUI_v2(root)
root.mainloop()
