import shlex
import sys

import pyrelight
from pyrelight import log, LogicError, PyrelightError
import pyrelight.sync
from pyrelight.sync import READONLY


def handle(args):
    if args.subcommand == "down":
        log("Exiting at user request.")
        pyrelight.global_exit = True
        return
    if args.subcommand == "songs":
        with pyrelight.sync.transact_metadata(READONLY) as metadata:
            pass
    raise LogicError(f"unexpected command: {args.subcommand}")
