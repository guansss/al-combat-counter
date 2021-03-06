import datetime
from typing import Callable

import win32con
import win32gui
import wx
from wx.lib.scrolledpanel import ScrolledPanel


def thread_safe(func: Callable):
    def wrapper(self, *args, **kw):

        def runner():
            try:
                return func(self, *args, **kw)
            except Exception as e:
                # catch and ignore the error of "wrapped C/C++ object of type <...> has been deleted"
                if 'has been deleted' not in str(e):
                    raise

        # self will be False when the wx.Window instance has been destroyed
        if self:
            return wx.CallAfter(runner)

    return wrapper


class App(wx.App):
    def __init__(self):
        super().__init__()

        self.control_panel = ControlFrame()
        self.display_panel = DisplayFrame(None, pos=(0, 0), point_size=23)

        self.control_panel.on_display_check = lambda checked: self.display_panel.Show(checked)
        self.control_panel.Bind(wx.EVT_CLOSE, self.on_exit)

        self.control_panel.Show()

    def on_exit(self, event: wx.CloseEvent):
        self.display_panel.Close(True)
        event.Skip()


class ControlFrame(wx.Frame):
    def __init__(self, parent=None, *args, **kw):
        super().__init__(
            parent,
            title='Azur Lane Combat Counter',
            style=wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.TAB_TRAVERSAL | wx.RESIZE_BORDER | wx.CLIP_CHILDREN,
            *args, **kw
        )

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))

        frame_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(frame_sizer)

        header_sizer = wx.BoxSizer(wx.HORIZONTAL)
        frame_sizer.Add(header_sizer, 0, wx.EXPAND | wx.ALL, border=5)

        self.spin = wx.SpinCtrl(self, min=0, max=99999,
                                style=wx.ALIGN_CENTER_HORIZONTAL | wx.SP_ARROW_KEYS | wx.SP_WRAP | wx.TE_PROCESS_ENTER)
        self.spin.SetFont(
            wx.Font(30, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Segoe UI"))
        self.spin.Bind(wx.EVT_SPINCTRL, lambda e: self.on_number_change(e.GetPosition()))
        self.spin.Bind(wx.EVT_TEXT, lambda e: self.on_number_change(e.GetInt()))

        header_sizer.Add(self.spin, 1, flag=wx.ALL)

        display_checkbox = wx.CheckBox(self, label='Display')
        display_checkbox.Bind(wx.EVT_CHECKBOX, lambda e: self.on_display_check(e.IsChecked()))

        header_sizer.Add(display_checkbox, flag=wx.CENTER | wx.LEFT | wx.RIGHT, border=40)

        info_panel = ScrolledPanel(self, style=wx.BORDER_THEME | wx.TAB_TRAVERSAL)
        info_panel.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENU))

        panel_sizer = wx.BoxSizer(wx.VERTICAL)
        info_panel.SetSizer(panel_sizer)

        self.info_text = wx.StaticText(info_panel)
        self.info_text.Wrap(-1)
        self.info_text.SetFocus()  # this removes focus from the SpinCtrl

        panel_sizer.Add(self.info_text, 0, wx.ALL, border=5)

        info_panel.Layout()
        info_panel.SetupScrolling()
        panel_sizer.FitInside(info_panel)
        frame_sizer.Add(info_panel, 1, wx.EXPAND | wx.ALL, border=5)

        self.Layout()
        self.Centre(wx.BOTH)

    @thread_safe
    def log(self, text: str):
        text = '[%s]  ' % datetime.datetime.now().strftime('%H:%M:%S') + text

        logged = self.info_text.GetLabelText()

        if not logged or len(logged) > 100000:
            logged = text
        else:
            logged = text + '\n' + logged

        self.info_text.SetLabelText(logged)

        panel = self.info_text.GetParent()
        panel.GetSizer().FitInside(panel)

    @thread_safe
    def set_number(self, number: int):
        self.spin.SetValue(number)

    def on_number_change(self, number: int):
        pass

    def on_display_check(self, checked: bool):
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

        font = self.text.GetFont()
        font.PointSize = point_size
        self.text.SetFont(font)

        sizer.Add(self.text, 0, wx.LEFT | wx.RIGHT, border=5)

    @thread_safe
    def display(self, text: str):
        # freeze/thaw also to prevent text flickering
        self.text.Freeze()
        self.text.SetLabelText(text)
        self.text.Thaw()

        self.GetSizer().Fit(self)
