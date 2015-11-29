import os
from functools import partial

from Tkinter import *
import ttk
from PIL import Image, ImageTk
from cStringIO import StringIO
import audiojack

audiojack.set_useragent('AudioJack-GUI v2', '0.1')

class AudioJackGUI_v2(object):
    def __init__(self, master):
        self.font = ('Segoe UI', 10)
        
        master.minsize(width=1280, height=720)
        self.mainframe = ttk.Frame(master)
        self.mainframe.pack()
        
        self.title = ttk.Label(self.mainframe, text='AudioJack', font=('Segoe UI Light', 24))
        self.title.pack()
        
        self.url = Text(self.mainframe, width=41, height=1, font=self.font, wrap=NONE)
        self.url.bind('<Return>', self.search)
        self.url.pack()
        
        self.submit = ttk.Button(self.mainframe, text='Go!', command=self.search)
        self.submit.pack()
    
    def reset(self):
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
    
    def search(self, event=None):
        self.reset()
        self.results = audiojack.get_results(self.url.get(0.0, END))
        self.results_frame = ttk.Frame(self.mainframe)
        self.results_label = ttk.Label(self.mainframe, text='Results:', font=self.font)
        self.results_label.pack()
        self.image_tk = []
        for i, result in enumerate(self.results[:8]):
            image_data = Image.open(StringIO(audiojack.get_cover_art_as_data(self.results[i][3]).decode('base64')))
            image_data = image_data.resize((200, 200), Image.ANTIALIAS)
            self.image_tk.append(ImageTk.PhotoImage(image=image_data))
        for i, result in enumerate(self.results[:8]):
            text = '%s\n%s\n%s' % (result[0], result[1], result[2])
            self.result = ttk.Button(self.results_frame, text=text, image=self.image_tk[i], compound=TOP, command=partial(self.download, i))
            self.result.grid(column=i%4, row=i/4)
        self.results_frame.pack()
        self.create_custom_frame()
    
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
    
    def download(self, index):
        self.reset()
        file = audiojack.select(index)
        text = 'Open %s' % file
        self.file = ttk.Button(self.mainframe, text=text, command=partial(self.open_file, file))
        self.results_label.pack_forget()
        self.results_label.destroy()
        self.results_frame.pack_forget()
        self.results_frame.destroy()
        self.file.pack()
    
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
