import os
import pathlib
import shlex
import sys

import pyrelight.cmdline
import pyrelight.server

print("Starting PYRELIGHT server.", file=sys.stderr)

os.chdir(pathlib.Path(__file__).parent.parent.resolve())


def respond(msg):
    args = shlex.split(msg)
    try:
        pyrelight.cmdline.parser.parse_args(args)
        result = "done"
    except Exception:
        return "error" + ("\n" + result if result else "")
    return "success" + ("\n" + result if result else "")


pyrelight.server.listen("server", respond)
