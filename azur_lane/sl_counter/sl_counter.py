import wx

from azur_lane.sl_counter.gui import DisplayPanel
from azur_lane.sl_counter.worker import Worker


def main():
    app = wx.App()

    display = DisplayPanel(pos=(0, 0), size=(200, 40))

    worker = Worker(display)
    worker.start()

    app.MainLoop()


if __name__ == '__main__':
    main()
