from Tkinter import *
from functools import partial
import audiojack
import os

#audiojack.set_useragent('name', 'version') MUST SET THIS

class App:
    def __init__(self, master):
        self.frame = Frame(master)
        self.frame.pack()
        
        self.title = Label(self.frame, text='AudioJack')
        self.title.pack()
        
        self.url = Label(self.frame, text='Enter URL: ')
        self.url.pack()
        self.urlInput = Entry(self.frame)
        self.urlInput.pack()

        self.submit = Button(self.frame, text='Go!', command=self.search)
        self.submit.pack()
    
    def search(self):
        results = audiojack.get_results(self.urlInput.get())
        self.results_frame = Frame(self.frame)
        for i, result in enumerate(results):
            text = '%s - %s [from %s]' % (result[0], result[1], result[2])
            self.result = Button(self.results_frame, text=text, command=partial(self.download, i))
            self.result.pack()
        self.results_frame.pack()
    
    def download(self, index):
        self.results_frame.destroy()
        file = audiojack.select(index)
        self.file = Button(self.frame, text=file, command=partial(self.openFile, file))
        self.file.pack()
    
    def openFile(self, file):
        os.startfile(file)

root = Tk()
root.configure()
app = App(root)
root.mainloop()