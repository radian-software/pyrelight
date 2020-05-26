import subprocess

import pyrelight
from pyrelight.util import run


default_gitignore = (
    """
/*
!/metadata.json
""".strip()
    + "\n"
)


def prepare():
    if run(["git", "rev-parse", "--git-dir"], check=False).returncode != 0:
        try:
            with open(pyrelight.root / ".gitignore", "x") as f:
                f.write(default_gitignore)
        except FileExistsError:
            pass
        run(["git", "init"])
        run(["git", "rev-parse", "--git-dir"])
    run(["git", "diff-files", "--quiet"])
    if run(["git", "rev-parse", "HEAD"], check=False).returncode != 0:
        run(["git", "ls-files"], check_no_output=True)
    else:
        run(["git", "diff-index", "--cached", "--quiet", "HEAD"])
    run(["git", "ls-files", "--others", "--exclude-standard"], check_no_output=True)


def commit(message):
    run(["git", "add", "--all"])
    if run(["git", "diff", "--name-only", "--cached"]).output:
        run(["git", "commit", "--allow-empty", "--message", message])
