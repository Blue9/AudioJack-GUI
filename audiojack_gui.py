import os
from functools import partial

from Tkinter import *
from PIL import Image, ImageTk
from cStringIO import StringIO
import audiojack

audiojack.set_useragent('AudioJack-GUI', '0.1')

class AudioJackGUI(object):
    def __init__(self, master):
        self.bg = '#124'
        
        master.minsize(width=1280, height=720)
        self.frame = Frame(master, bg=self.bg)
        self.frame.pack(fill=BOTH, expand=1)

        self.font = ('Segoe UI', 10)
        
        self.title = Label(self.frame, text='AudioJack', font=('Segoe UI Light', 24), fg='#fff', bg=self.bg)
        self.title.pack()
        
        self.url = Label(self.frame, text='Enter YouTube or SoundCloud URL', font=self.font, fg='#fff', bg=self.bg)
        self.url.pack()
        self.url_input = Entry(self.frame)
        self.url_input.pack()

        self.submit = Button(self.frame, text='Go!', font=self.font, fg='#fff', bg='#20648f', activeforeground='#fff', activebackground='#1a5274', command=self.search)
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
    
    def search(self):
        self.reset()
        self.results = audiojack.get_results(self.url_input.get())
        self.results_frame = Frame(self.frame, bg=self.bg)
        self.results_label = Label(self.frame, text='Results:', font=self.font, bg=self.bg, fg='#fff')
        self.results_label.pack()
        self.image_tk = []
        for i, result in enumerate(self.results[:8]):
            image_data = Image.open(StringIO(audiojack.get_cover_art_as_data(self.results[i][3]).decode('base64')))
            image_data = image_data.resize((200, 200), Image.ANTIALIAS)
            self.image_tk.append(ImageTk.PhotoImage(image=image_data))
        for i, result in enumerate(self.results[:8]):
            text = '%s\n%s\n%s' % (result[0], result[1], result[2])
            self.result = Button(self.results_frame, text=text, font=self.font, fg='#fff', bg='#444', activeforeground='#fff', activebackground='#111', cursor='bottom_side', image=self.image_tk[i], highlightbackground='#444', highlightthickness=4, compound=TOP, command=partial(self.download, i))
            self.result.bind('<Enter>', partial(self.result_hover, self.result))
            self.result.bind('<Leave>', partial(self.result_leave, self.result))
            self.result.grid(column=i%4, row=i/4)
        self.results_frame.pack()
        self.create_custom_frame()
    
    def result_hover(self, button, event):
        button.config(bg='#222')
    
    def result_leave(self, button, event):
        button.config(bg='#444')
    
    def create_custom_frame(self):
        self.custom_frame = Frame(self.frame, bg=self.bg)
        self.custom_title = Label(self.custom_frame, fg='#fff', bg=self.bg, text='Custom tags:', font=self.font)
        self.artist_label = Label(self.custom_frame, fg='#fff', bg=self.bg, text='Artist: ', font=self.font)
        self.artist_input = Entry(self.custom_frame, fg='#000', font=self.font)
        self.title_label = Label(self.custom_frame, fg='#fff', bg=self.bg, text='Title: ', font=self.font)
        self.title_input = Entry(self.custom_frame, fg='#000', font=self.font)
        self.album_label = Label(self.custom_frame, fg='#fff', bg=self.bg, text='Album: ', font=self.font)
        self.album_input = Entry(self.custom_frame, fg='#000', font=self.font)
        self.custom_submit = Button(self.custom_frame, text='Download using custom tags', font=self.font, fg='#fff', bg='#20648f', activeforeground='#fff', activebackground='#1a5274', command=self.custom)
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
        self.file = Button(self.frame, text=file, command=partial(self.openFile, file))
        self.file.pack()
    
    def custom(self):
        artist = self.artist_input.get()
        title = self.title_input.get()
        album = self.album_input.get()
        self.reset()
        file = audiojack.custom(artist, title, album)
        self.file = Button(self.frame, text=file, font=self.font, command=partial(self.openFile, file))
        if file == '':
            file == 'Song.mp3'
        self.file.pack()
    
    def openFile(self, file):
        os.startfile(file)

root = Tk()
root.title('AudioJack-GUI Beta')
app = AudioJackGUI(root)
root.mainloop()