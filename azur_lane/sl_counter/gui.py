from typing import Callable

import wx


# is this necessary?
def call_after(func: Callable):
    def wrapper(*args, **kw):
        return wx.CallAfter(func, *args, **kw)

    return wrapper


class ControlPanel(object):
    frame: wx.Frame

    def __init__(self):
        self.frame = wx.Frame(None, title='Azur Lane SL Counter')
        self.frame.Show()


class DisplayPanel(object):
    frame: wx.Frame
    text: wx.StaticText

    def __init__(self, size=(200, 40), *args, **kw):
        style = wx.STAY_ON_TOP | wx.BORDER_NONE
        self.frame = wx.Frame(None, style=style, size=size, *args, **kw)

        self.frame.SetTransparent(200)
        self.frame.SetBackgroundColour('black')

        self.text = wx.StaticText(self.frame)
        self.text.SetForegroundColour('white')
        self.text.SetTransparent(100)
        print(self.text.CanSetTransparent())

        font = self.text.Font
        font.PointSize = size[1] / 1.7  # divided by line height
        self.text.Font = font

        self.frame.Show()

    def display(self, text: str):
        self.text.SetLabelText(text)
