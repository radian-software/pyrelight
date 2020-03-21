import shlex
import sys

import pyrelight
from pyrelight import log, LogicError, PyrelightError


def handle(args):
    if args.subcommand == "down":
        log("Exiting at user request.")
        pyrelight.global_exit = True
        return
    raise LogicError(f"unexpected command: {args.subcommand}")
