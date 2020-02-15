import wx

from azur_lane.challenge_counter.gui import DisplayFrame, ControlFrame, App
from azur_lane.challenge_counter.worker import Worker


def main():
    app = App()

    worker = Worker()
    worker.start()

    app.MainLoop()


if __name__ == '__main__':
    main()
