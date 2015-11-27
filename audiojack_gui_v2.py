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
        
        self.title = ttk.Label(self.mainframe, text='AudioJack')
        self.title.pack()
        
        self.url = Text(self.mainframe, width=41, height=1, font=self.font, wrap=NONE)
        self.url.pack()
        
        self.submit = ttk.Button(self.mainframe, text='Go!', command=self.search)
        self.submit.pack()
    
    def search(self):
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
    
    def download(self, index):
        file = audiojack.select(index)
        text = 'Open %s' % file
        self.file = ttk.Button(self.mainframe, text=text, command=partial(self.open_file, file))
        self.results_frame.pack_forget()
        self.results_frame.destroy()
        self.file.pack()
    
    def open_file(self, file):
        os.startfile(file)

root = Tk()
root.title('AudioJack-GUI v2')
app = AudioJackGUI_v2(root)
root.mainloop()
