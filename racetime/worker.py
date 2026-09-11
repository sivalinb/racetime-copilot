"""Run: python -m racetime.worker. Durable jobs survive UI refreshes."""

import signal
import time

from .service import Service

running = True


def stop(*_):
    global running
    running = False


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    service = Service()
    while running:
        if not service.process_one():
            time.sleep(1)
