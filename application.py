from threading import RLock
from audiojack import AudioJack


class AudioJackApplication(object):
    def __init__(self):
        self.lock = RLock()
        self.observers = []
        self.requests = []  # Used to record all previous searches, could be used for some features

    def add_observer(self, observer):
        self.observers.append(observer)

    @property
    def last_search(self):
        try:
            self.lock.acquire()
            if len(self.requests) > 0:
                return self.requests[-1]
            else:
                return None
        finally:
            self.lock.release()

    def search(self, url):
        search = SearchRequest(url)
        try:
            self.lock.acquire()
            self.requests.append(search)
        finally:
            self.lock.release()
        self.notify()

    def select(self, index):
        try:
            self.lock.acquire()
            self.last_search.select(index)
        finally:
            self.lock.release()
        self.notify()

    def notify(self):
        for observer in self.observers:
            observer.notify()


class SearchRequest(object):
    def __init__(self, url=None):
        self.error = 0
        self.results = None
        self.selection = None
        self.file = None
        self.audiojack = AudioJack(small_cover_art=True)
        self.url = url
        if url:
            self.search(url)

    def search(self, url):
        try:
            self.results = self.audiojack.get_results(url)
        except AttributeError as e:
            print(e)
            self.error = 1

    def select(self, index, path=None):
        self.selection = self.results[index]
        try:
            self.file = self.audiojack.select(self.selection, path=path)
        except AttributeError as e:
            print(e)
            self.error = 1

    def custom(self, title, artist, album, path=None):
        try:
            self.file = self.audiojack.select({
                'url': self.url,
                'title': title,
                'artist': artist,
                'album': album
            }, path=path)
        except AttributeError as e:
            print(e)
            self.error = 1

    def cut_file(self, start, end):
        self.audiojack.cut_file(self.file, start, end)
