import re
import threading
import time
from typing import NewType, Optional, Tuple

import win32gui

Handle = NewType('Handle', int)


class Worker(threading.Thread):
    def __init__(self):
        super().__init__()

        self.setDaemon(True)

        self.count = 0

    def run(self):
        self.setup()

        while True:
            self.count += 1
            self.on_count(self.count)
            time.sleep(1)

    def setup(self):
        hwnd, title = get_window('MuMu')

        if hwnd:
            self.log('Find window [%s]' % title)

            mumu = MuMuWindow(hwnd)

    def log(self, text: str):
        pass

    def on_count(self, number: int):
        pass


class MuMuWindow(object):

    def __init__(self, hwnd: Handle):
        pass


def get_window(title_pattern: str) -> Tuple[Optional[Handle], str]:
    reg = re.compile(title_pattern)
    hwnd: Optional[Handle] = None
    title = ''

    def handler(_hwnd: Handle, _):
        nonlocal hwnd
        nonlocal title

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

    return hwnd, title
