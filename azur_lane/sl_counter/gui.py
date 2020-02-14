from typing import Callable

import win32con
import win32gui
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

        # let the frame can be clicked through, which means it won't block mouse events
        # http://wxwidgets.10942.n7.nabble.com/wxPython-and-pywin32-Implementing-on-top-transparency-and-click-through-on-Windows-tp30543.html
        hwnd = self.frame.GetHandle()
        extended_style_settings = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                               extended_style_settings | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
        win32gui.SetLayeredWindowAttributes(hwnd, 0, 255, win32con.LWA_ALPHA)

        self.frame.SetTransparent(200)
        self.frame.SetBackgroundColour('black')

        self.text = wx.StaticText(self.frame)
        self.text.SetForegroundColour('white')

        font = self.text.Font
        font.PointSize = size[1] / 1.7  # divided by line height
        self.text.Font = font

        self.frame.Show()

    def display(self, text: str):
        self.text.SetLabelText(text)
