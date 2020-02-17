import collections
import math
import re
import sys
import threading
import time
from typing import NewType, Optional, Tuple, List, Callable

import win32gui

sys.path.append('../../')  # noqa: E402

from utils.graphic import unpack_rgb_from_colorref

Handle = NewType('Handle', int)
RGBColor = collections.namedtuple('Color', ['r', 'g', 'b'])


class Worker(threading.Thread):
    def __init__(self, logger: Callable[[str], None]):
        super().__init__()

        self.setDaemon(True)

        self.logger = logger
        self.count = 0

        try:
            self.game_window = MuMuWindow(logger)
            self.game_window.on_combat_loading_completed = self.increase_count
        except Exception as e:
            self.logger('E: ' + str(e))

    def run(self):
        while True:
            try:
                self.game_window.update()
            except Exception as e:
                self.logger('E: ' + str(e))

            time.sleep(0.5)

    def increase_count(self):
        self.count += 1
        self.on_count(self.count)

    def on_count(self, number: int):
        pass


'''
A loading scene is like:
┌────────────────────────────────────────────┐
│                                            │
│                                            │
│  ###############=========================  │  <- progress bar (40 sample points)
└────────────────────────────────────────────┘

where # represents the foreground color and = represents the background color
'''

PROGRESS_FG_COLOR = (90, 154, 255)  # RGB
PROGRESS_BG_COLOR = (224, 224, 224)  # RGB

COLOR_COMPARE_TOLERANCE = math.dist((0, 0, 0), (40, 40, 40))

PROGRESS_SAMPLE_POINTS_AMOUNT = 6
PROGRESS_RECOGNITION_REQUIRED_POINTS = 4  # the minimum points required for the sum of foreground and background
PROGRESS_RECOGNITION_REQUIRED_POINTS_EACH = 2  # the minimum points required for each of foreground and background

# the coordinates were recorded in 2560*1440 resolution
PROGRESS_Y = 1356 / 1440
PROGRESS_SAMPLE_POINTS_X = [
    (80 + (2560 - 80 * 2) * i / PROGRESS_SAMPLE_POINTS_AMOUNT) / 2560
    for i in range(0, PROGRESS_SAMPLE_POINTS_AMOUNT)
]

DETECTION_COOL_DOWN = 3  # seconds


class GameWindow(object):
    def __init__(self, logger: Callable[[str], None]):
        self.logger = logger

        self.canvas_hwnd = Handle(0)
        self.canvas_hdc = Handle(0)

        self.combat_loading = False
        self.next_detection_time = 0

    def _setup_window(self):
        """ Assigns canvas_hwnd and canvas_hdc. """
        raise NotImplementedError()

    def update(self):
        if not win32gui.IsWindow(self.canvas_hwnd):
            self._setup_window()

            # postpone detection
            return

        now = time.time()

        if self.combat_loading or now >= self.next_detection_time:
            sample_colors = self.get_sample_colors()

            fg_point_amount = bg_point_amount = 0

            for i in range(PROGRESS_SAMPLE_POINTS_AMOUNT):
                if math.dist(sample_colors[i], PROGRESS_FG_COLOR) <= COLOR_COMPARE_TOLERANCE:
                    fg_point_amount += 1
                else:
                    break

            for j in range(i, PROGRESS_SAMPLE_POINTS_AMOUNT):
                if math.dist(sample_colors[j], PROGRESS_BG_COLOR) <= COLOR_COMPARE_TOLERANCE:
                    bg_point_amount += 1

            # visualize detected progress bar
            # print(''.join(list(
            #     map(lambda color:
            #         '#' if math.dist(color, PROGRESS_FG_COLOR) <= COLOR_COMPARE_TOLERANCE
            #         else '=' if math.dist(color, PROGRESS_BG_COLOR) <= COLOR_COMPARE_TOLERANCE
            #         else ' ',
            #         sample_colors
            #         ))), fg_point_amount, bg_point_amount, self.combat_loading)

            if fg_point_amount + bg_point_amount >= PROGRESS_RECOGNITION_REQUIRED_POINTS \
                    and fg_point_amount >= PROGRESS_RECOGNITION_REQUIRED_POINTS_EACH \
                    and bg_point_amount >= PROGRESS_RECOGNITION_REQUIRED_POINTS_EACH:  # recognize the progress bar
                self.combat_loading = True
                self.next_detection_time = now + DETECTION_COOL_DOWN
            else:
                if self.combat_loading:
                    self.on_combat_loading_completed()

                self.combat_loading = False

    def get_sample_colors(self) -> List[RGBColor]:
        (left, top, right, bottom) = win32gui.GetWindowRect(self.canvas_hwnd)
        width = right - left
        height = bottom - top

        # convert relative coordinate to absolute coordinate in window
        y = int(height * PROGRESS_Y)

        return [
            unpack_rgb_from_colorref(win32gui.GetPixel(self.canvas_hdc, int(x * width), y))
            for x in PROGRESS_SAMPLE_POINTS_X
        ]

    def on_combat_loading_completed(self):
        pass


class MuMuWindow(GameWindow):
    def _setup_window(self):
        hwnd, title = get_window('MuMu')

        if hwnd:
            self.canvas_hwnd, _ = get_window('canvas', hwnd)

            if self.canvas_hwnd:
                self.logger('Find window [%s]' % title)
                self.canvas_hdc = win32gui.GetDC(self.canvas_hwnd)
            else:
                self.logger('Find window [%s] but canvas is not ready' % title)
        else:
            self.logger('Could not find window')


def get_window(title_pattern: str, parent: Optional[Handle] = None) -> Tuple[Handle, str]:
    reg = re.compile(title_pattern)
    hwnd = Handle(0)
    title = ''

    def handler(_hwnd: Handle, _):
        nonlocal hwnd
        nonlocal title

        title = win32gui.GetWindowText(_hwnd)

        if reg.search(title):
            hwnd = _hwnd
            return False

    try:
        win32gui.EnumChildWindows(parent, handler, None)
    except BaseException as e:
        # swallow the error that will be mysteriously thrown when breaking the window enumeration by returning False
        # in handler, its error code can be 0 or 126
        if getattr(e, 'winerror', -1) not in (0, 126):
            raise

    return hwnd, title
