import os

# make the script runnable from anywhere
os.chdir(os.path.dirname(__file__))  # noqa: E402

from gui import App
from worker import Worker
from server import Server


def main():
    app = App()

    worker = Worker(lambda text: app.control_panel.log(text))
    worker.start()

    server = Server(os.getcwd())
    server.start()

    def on_count(number: int):
        app.display_panel.display('出击次数：%d' % number)
        app.control_panel.set_number(number)

        server.send(str(number))

        try:
            with open('record.txt', 'w') as w:
                w.write(str(number))
        except Exception as e:
            app.control_panel.log(str(e))

    record = 0

    worker.on_count = on_count

    def on_number_change(number: int):
        # this is not thread-safe and can cause inconsistency, but it does'nt matter in this project
        setattr(worker, 'count', number)
        on_count(number)  # manually update the display

    try:
        with open('record.txt', 'r') as r:
            record = int(r.read() or 0)
    except Exception:
        pass

    on_number_change(record)  # display initially

    app.control_panel.on_number_change = on_number_change

    app.MainLoop()


if __name__ == '__main__':
    main()
