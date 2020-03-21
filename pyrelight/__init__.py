import datetime
import sys


global_exit = False


class LogicError(Exception):
    pass


class PyrelightError(Exception):
    pass


def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}", file=sys.stderr)
