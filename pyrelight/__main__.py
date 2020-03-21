import os
import pathlib
import shlex
import sys
import traceback

import pyrelight.cmdline
import pyrelight.server

print("Starting PYRELIGHT server.", file=sys.stderr)

os.chdir(pathlib.Path(__file__).parent.parent.resolve())


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
            status = "success"
            output += "done\n"
    except Exception as e:
        status = "error"
        output += traceback.format_exc()
    return status + ("\n" + output if output else "")


pyrelight.server.listen("server", respond)
