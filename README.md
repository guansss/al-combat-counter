# Azur Lane Combat Counter

Automatic combat recording for Azur Lane.

![preview](preview.jpg)

**PVP combats are also counted.**

Quitting the combat before it ends does not prevent counter's increasing.

Recognition may not succeed when the emulator window is too small.

## Usage

Just keep both `combat_counter.pyw` and your emulator running. The counter will increase when a combat starts.

## Emulator Recognition

Currently only MuMu Emulator is supported for recognition. To support another emulator, you can inherit the `GameWindow` class and replace the constructor in `Worker.__init__()`.

```python
class MyGameWindow(GameWindow):
    def _setup_window(self):
        hwnd, title = get_window('My Emulator')

        # for example the game screen is represented by a child window named "canvas"
        self.canvas_hwnd, _ = get_window('canvas', hwnd)
        self.canvas_hdc = win32gui.GetDC(self.canvas_hwnd)

# in Worker.__init__()
self.game_window = MyGameWindow(logger)
```

## OBS Streaming

Make sure the script is running to get this working.

1. Add a browser source, set URL to `http://127.0.0.1:8888/`.
2. Set size to `300, 40` or whatever you think better.
3. Append `#text { background: none }` to the custom CSS of browser source if you want a transparent background.
