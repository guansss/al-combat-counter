from azur_lane.challenge_counter.gui import App
from azur_lane.challenge_counter.worker import Worker


def main():
    app = App()

    worker = Worker(lambda text: app.control_panel.log(text))

    def on_count(number: int):
        app.display_panel.display('挑战次数：%d' % number)
        app.control_panel.set_number(number)

    on_count(0)  # display initially

    worker.on_count = on_count

    def on_number_change(number: int):
        # this is not thread-safe and can cause inconsistency, but it does'nt matter in this project
        setattr(worker, 'count', number)
        on_count(number)  # manually update the display

    app.control_panel.on_number_change = on_number_change

    worker.start()

    app.MainLoop()


if __name__ == '__main__':
    main()
