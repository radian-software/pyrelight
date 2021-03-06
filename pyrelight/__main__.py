import os
import pathlib
import shlex
import sys
import traceback

from pyrelight import log, PyrelightError
import pyrelight.cmdline
import pyrelight.commands
import pyrelight.server

log("Starting Pyrelight server...")

os.chdir(pathlib.Path(__file__).parent.parent.resolve())

if "PYRELIGHT_HOME" not in os.environ:
    log("You need to set PYRELIGHT_HOME before starting the server.")
    sys.exit(1)

pyrelight.root = pathlib.Path(os.environ["PYRELIGHT_HOME"]).resolve()

if not pyrelight.root.is_dir():
    log(f"Directory does not exist: PYRELIGHT_HOME={pyrelight.root}")
    sys.exit(1)


def respond(msg):
    cmdline = shlex.split(msg)
    output = ""
    try:
        args, parser_output = pyrelight.cmdline.parse_cmdline(cmdline)
        output += parser_output
        if args is True:  # exit with success, e.g. from --help
            status = "success"
        elif args is False:  # exit with failure, e.g. from invalid arguments
            status = "error"
        else:
            log("> " + " ".join(map(shlex.quote, cmdline)))
            response = pyrelight.commands.handle(args)
            if response:
                output += response
            status = "success"
    except PyrelightError as e:
        status = "error"
        output += f"pyrelight: {str(e)}\n"
    except Exception as e:
        status = "error"
        output += traceback.format_exc()
    return status + "\n" + output


pyrelight.server.listen("server", respond)
