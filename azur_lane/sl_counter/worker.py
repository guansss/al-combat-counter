import re
import threading
import time
from typing import NewType, Optional

import win32gui

from azur_lane.sl_counter.gui import DisplayPanel

Handle = NewType('Handle', int)


class Worker(threading.Thread):
    display: DisplayPanel

    def __init__(self, display: DisplayPanel):
        super().__init__()

        self.display = display
        self.setDaemon(True)

    def run(self):
        time.sleep(0.5)
        self.setup()

    def setup(self):
        hwnd = get_window('MuMu')

        if hwnd:
            mumu = MuMuWindow(hwnd)

            self.display.display('SL次数')


class MuMuWindow(object):

    def __init__(self, hwnd: Handle):
        pass


def get_window(title_pattern: str) -> Optional[Handle]:
    reg = re.compile(title_pattern)
    hwnd: Optional[Handle] = None

    def handler(_hwnd: Handle, _):
        nonlocal hwnd

        title = win32gui.GetWindowText(_hwnd)

        if reg.search(title):
            hwnd = _hwnd
            return False

    try:
        win32gui.EnumWindows(handler, None)
    except BaseException as e:
        # swallow the error that will be mysteriously thrown when breaking the window enumeration by returning False
        # in handler, its error code can be 0 or 126
        if getattr(e, 'winerror', -1) not in (0, 126):
            raise

    return Handle(hwnd)
