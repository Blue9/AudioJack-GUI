import os
from functools import partial

from Tkinter import *
from PIL import Image, ImageTk
from cStringIO import StringIO
import audiojack

audiojack.set_useragent('AudioJack-GUI', '0.1')

class AudioJackGUI(object):
    def __init__(self, master):
        self.frame = Frame(master)
        self.frame.pack()
        
        self.title = Label(self.frame, text='AudioJack')
        self.title.pack()
        
        self.url = Label(self.frame, text='Enter Youtube or SoundCloud URL: ')
        self.url.pack()
        self.urlInput = Entry(self.frame)
        self.urlInput.pack()

        self.submit = Button(self.frame, text='Go!', command=self.search)
        self.submit.pack()
    
    def search(self):
        self.results = audiojack.get_results(self.urlInput.get())
        self.results_frame = Frame(self.frame)
        for i, result in enumerate(self.results):
            text = '%s - %s [from %s]' % (result[0], result[1], result[2])
            self.result = Button(self.results_frame, text=text, command=partial(self.download, i))
            self.result.bind('<Enter>', partial(self.showImage, i))
            self.result.bind('<Leave>', self.hideImage)
            self.result.pack()
        self.results_frame.pack()
    
    def showImage(self, index, event):
        self.image_frame = Frame(self.frame)
        self.image_frame.config(height=200)
        self.image_frame.pack()
        
        image_data = Image.open(StringIO(audiojack.get_cover_art_as_data(self.results[index][3]).decode('base64')))
        image_data = image_data.resize((200,200), Image.ANTIALIAS)
        self.image_tk = ImageTk.PhotoImage(image=image_data)
        self.image = Label(self.image_frame, image=self.image_tk, height=200, width=200, background='#000')
        self.image.pack()
    
    def hideImage(self, event):
        self.image_frame.pack_forget()
        self.image.pack_forget()
        self.image.destroy()
    
    def download(self, index):
        self.results_frame.pack_forget()
        self.results_frame.destroy()
        self.image_frame.pack_forget()
        self.image_frame.destroy()
        file = audiojack.select(index)
        self.file = Button(self.frame, text=file, command=partial(self.openFile, file))
        self.file.pack()
    
    def openFile(self, file):
        os.startfile(file)

root = Tk()
root.title('AudioJack-GUI Beta')
app = AudioJackGUI(root)
root.mainloop()