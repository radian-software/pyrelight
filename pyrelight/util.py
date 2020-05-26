import collections
import shlex
import subprocess

import pyrelight
from pyrelight import PyrelightError


PyrelightSubprocessResult = collections.namedtuple(
    "PyrelightSubprocessResult", ["returncode", "output"]
)


def quote_cmdline(cmdline):
    return " ".join(map(shlex.quote, cmdline))


def run(cmdline, check=True, check_no_output=False, **kwargs):
    try:
        result = subprocess.run(
            cmdline,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            cwd=pyrelight.root,
            **kwargs,
        )
    except OSError as e:
        raise PyrelightError(
            f"command failed: {e}\ncommand: {quote_cmdline(cmdline)}"
        ) from None
    output = result.stdout.decode(errors="replace").strip()
    if check and result.returncode != 0:
        info = f"command failed with return code {result.returncode}"
        if output:
            info += f"\noutput: {output}"
        raise PyrelightError(info)
    if check_no_output and output:
        raise PyrelightError(
            f"command produced output when it should not have\ncommand: {quote_cmdline(cmdline)}\noutput: {output}"
        )
    return PyrelightSubprocessResult(returncode=result.returncode, output=output)
