from application import AudioJackApplication
from audiojack_gui import AudioJackGUI


def launch():
    application = AudioJackApplication()
    gui = AudioJackGUI()

    application.add_observer(gui)  # GUI is notified when application changes
    gui.audiojack = application

    gui.run()


if __name__ == '__main__':
    launch()
