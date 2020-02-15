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
        self.display_panel = DisplayFrame(None, pos=(0, 0), point_size=23)

        self.display_panel.Show()
        self.control_panel.Show()


class ControlFrame(wx.Frame):
    def __init__(self, parent=None, *args, **kw):
        super().__init__(
            parent,
            title='Azur Lane Challenge Counter',
            style=wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.TAB_TRAVERSAL | wx.RESIZE_BORDER | wx.CLIP_CHILDREN,
            *args, **kw
        )

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))

        self.spin = wx.SpinCtrl(self, min=0, max=99999,
                                style=wx.ALIGN_CENTER_HORIZONTAL | wx.SP_ARROW_KEYS | wx.SP_WRAP | wx.TE_PROCESS_ENTER)
        self.spin.SetFont(
            wx.Font(30, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Segoe UI"))
        self.spin.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.spin.Bind(wx.EVT_TEXT, self.on_spin_text)

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

    def set_number(self, number: int):
        self.spin.Value = number

    def on_spin(self, event: wx.SpinEvent):
        self.on_number_change(event.GetPosition())

    def on_spin_text(self, event: wx.CommandEvent):
        self.on_number_change(event.GetInt())

    def on_number_change(self, number: int):
        pass


class DisplayFrame(wx.Frame):
    def __init__(self, parent=None, point_size=23, *args, **kw):
        super().__init__(parent, style=wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP | wx.BORDER_NONE | wx.CLIP_CHILDREN, *args,
                         **kw)

        # let the frame can be clicked through, which means it won't block mouse events
        # http://wxwidgets.10942.n7.nabble.com/wxPython-and-pywin32-Implementing-on-top-transparency-and-click-through-on-Windows-tp30543.html
        hwnd = self.GetHandle()
        extended_style_settings = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                               extended_style_settings | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
        win32gui.SetLayeredWindowAttributes(hwnd, 0, 255, win32con.LWA_ALPHA)

        # prevent text flickering
        self.SetDoubleBuffered(True)

        self.SetTransparent(200)
        self.SetBackgroundColour('black')

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        self.text = wx.StaticText(self)
        self.text.SetForegroundColour('white')

        font = self.text.Font
        font.PointSize = point_size
        self.text.Font = font

        sizer.Add(self.text, 0, wx.LEFT | wx.RIGHT, border=5)

    def display(self, text: str):
        # freeze/thaw also to prevent text flickering
        self.text.Freeze()
        self.text.SetLabelText(text)
        self.text.Thaw()
        self.GetSizer().Fit(self)
