import os
import pathlib
import sys

import pyrelight.server

print("Starting PYRELIGHT server.", file=sys.stderr)

os.chdir(pathlib.Path(__file__).parent.parent.resolve())

pyrelight.server.listen("server", lambda msg: "echoing: " + msg)
