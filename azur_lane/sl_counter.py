import re
from typing import NewType, Optional

import win32gui

Handle = NewType('Handle', int)


def main():
    hwnd = get_window('MuMu')


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
        if not (hasattr(e, 'winerror') and (e.winerror == 0 or e.winerror == 126)):
            raise

    return Handle(hwnd)


if __name__ == '__main__':
    main()
