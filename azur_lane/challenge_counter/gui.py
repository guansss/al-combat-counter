from typing import Callable

import win32con
import win32gui
import wx


# is this necessary?
def call_after(func: Callable):
    def wrapper(*args, **kw):
        return wx.CallAfter(func, *args, **kw)

    return wrapper


class App(wx.App):

    def __init__(self):
        super().__init__()

        self.control_panel = ControlFrame()
        self.display_panel = DisplayFrame(self.control_panel, pos=(0, 0), size=(200, 40))

        self.display_panel.Show()
        self.control_panel.Show()


class ControlFrame(wx.Frame):
    def __init__(self, parent=None, *args, **kw):
        super().__init__(
            parent,
            title='Azur Lane Challenge Counter',
            style=wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.TAB_TRAVERSAL | wx.RESIZE_BORDER,
            *args, **kw
        )

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))

        self.spin = wx.SpinCtrl(self, min=0, max=9999, style=wx.ALIGN_CENTER_HORIZONTAL | wx.SP_ARROW_KEYS | wx.SP_WRAP)
        self.spin.SetFont(
            wx.Font(30, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Segoe UI"))

        frame_sizer = wx.BoxSizer(wx.VERTICAL)
        frame_sizer.Add(self.spin, flag=wx.ALIGN_CENTER | wx.ALL, border=5)

        info_panel = wx.Panel(self, style=wx.BORDER_THEME | wx.TAB_TRAVERSAL)
        panel_sizer = wx.BoxSizer(wx.VERTICAL)

        self.info_text = wx.StaticText(info_panel)
        self.info_text.Wrap(-1)

        panel_sizer.Add(self.info_text, 0, wx.ALL, 5)

        info_panel.SetSizer(panel_sizer)
        info_panel.Layout()
        panel_sizer.Fit(info_panel)
        frame_sizer.Add(info_panel, 1, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(frame_sizer)
        self.Layout()
        self.Centre(wx.BOTH)

    def info(self, text: str):
        self.info_text.SetLabelText(text)


class DisplayFrame(wx.Frame):
    def __init__(self, parent=None, size=(200, 40), *args, **kw):
        super().__init__(parent, size=size, style=wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP | wx.BORDER_NONE, *args, **kw)

        # let the frame can be clicked through, which means it won't block mouse events
        # http://wxwidgets.10942.n7.nabble.com/wxPython-and-pywin32-Implementing-on-top-transparency-and-click-through-on-Windows-tp30543.html
        hwnd = self.GetHandle()
        extended_style_settings = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                               extended_style_settings | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
        win32gui.SetLayeredWindowAttributes(hwnd, 0, 255, win32con.LWA_ALPHA)

        self.SetTransparent(200)
        self.SetBackgroundColour('black')

        self.text = wx.StaticText(self)
        self.text.SetForegroundColour('white')

        font = self.text.Font
        font.PointSize = size[1] / 1.7  # divided by line height
        self.text.Font = font

    def display(self, text: str):
        self.text.SetLabelText(text)
