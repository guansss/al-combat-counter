from azur_lane.challenge_counter.gui import App
from azur_lane.challenge_counter.worker import Worker


def main():
    app = App()

    worker = Worker(lambda text: app.control_panel.log(text))

    def worker_on_count(number: int):
        app.display_panel.display('挑战次数：%d' % number)
        app.control_panel.set_number(number)

    worker_on_count(0)  # display initially

    worker.on_count = worker_on_count

    app.control_panel.on_number_change = lambda number: setattr(worker, 'count', number)

    worker.start()

    app.MainLoop()


if __name__ == '__main__':
    main()
