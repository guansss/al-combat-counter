from typing import Tuple


def unpack_rgb(value: int) -> Tuple[int, int, int]:
    """ https://stackoverflow.com/a/2262117 """

    return value // 256 // 256 % 256, value // 256 % 256, value % 256


def unpack_rgb_from_colorref(value: int) -> Tuple[int, int, int]:
    """
    The COLORREF has an inverse RGB sequence, which is BBGGRR.
    https://docs.microsoft.com/en-us/windows/win32/gdi/colorref
    """

    return value % 256, value // 256 % 256, value // 256 // 256 % 256
