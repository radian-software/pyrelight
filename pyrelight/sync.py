import contextlib
import json
import os
import pathlib
import subprocess

import pyrelight
from pyrelight import PyrelightError
import pyrelight.database
import pyrelight.git


READONLY = None

metadata_file = pyrelight.root / "metadata.json"
session_file = pyrelight.root / "session.json"
history_file = pyrelight.root / "history.json"

g_metadata_mtime = -1
g_session_mtime = -1
g_history_mtime = -1


def read_metadata():
    """
    Read the metadata file into memory synchronously. If the file
    doesn't exist, use a default value for the metadata.
    """
    global g_metadata_mtime
    try:
        with open(metadata_file) as f:
            g_metadata_mtime = os.fstat(f.fileno())
            metadata = json.load(f)
            version = metadata["version"]
            if version != 1:
                raise PyrelightError(f"unexpected metadata version: {version}")
            pyrelight.database.g_metadata = metadata
    except FileNotFoundError:
        g_metadata_mtime = 0
        pyrelight.database.g_metadata = pyrelight.database.metadata_default


def read_metadata_maybe():
    """
    If the metadata file has changed since the last sync, or if this
    is the first sync, read the metadata file into memory.
    """
    try:
        disk_mtime = metadata_file.stat().st_mtime
    except FileNotFoundError:
        disk_mtime = 0
    if disk_mtime > g_metadata_mtime:
        read_metadata()


def write_metadata():
    """
    Write the metadata file from memory atomically.
    """
    tmp_file = pathlib.Path(str(metadata_file) + ".tmp")
    with open(tmp_file) as f:
        json.dump(pyrelight.database.g_metadata, f)
    tmp_file.rename(metadata_file)


@contextlib.contextmanager
def transact_metadata(message):
    """
    Context manager to handle all the bookkeeping around reading and
    writing the metadata file, including revision control. If message
    is READONLY, assume no changes will be made to the metadata, and
    don't write it back.
    """
    pyrelight.git.prepare()
    read_metadata_maybe()
    yield pyrelight.database.g_metadata
    if message:
        write_metadata(message)
        pyrelight.git.commit(message)
