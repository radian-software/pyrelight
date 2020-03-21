import os
import pathlib
import shlex
import sys

import pyrelight.cmdline
import pyrelight.server

print("Starting PYRELIGHT server.", file=sys.stderr)

os.chdir(pathlib.Path(__file__).parent.parent.resolve())

pyrelight.server.listen(
    "server", lambda msg: repr(pyrelight.cmdline.parser.parse_args(shlex.split(msg))),
)
