import argparse


class ArgumentParserExit(Exception):
    def __init__(self, status):
        self.status = status


# Yuck. Blame argparse. I can't do it with a class-local variable
# because multiple instances of ArgumentParser are involved when
# dealing with subcommands.
global_output = None


class FriendlyArgumentParser(argparse.ArgumentParser):
    def _print_message(self, message, file=None):
        global global_output
        if message:
            global_output += message

    def exit(self, status=0, message=None):
        self._print_message(message)
        raise ArgumentParserExit(status=status)


class StoreConstPlusAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, val_dest=None, **kwargs):
        self.val_dest = val_dest if val_dest is not None else dest
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, self.const)
        setattr(namespace, self.val_dest, values)


parser = FriendlyArgumentParser(
    prog="plt", description="Fast command-line music library manager and media player.",
)
subparsers = parser.add_subparsers(
    dest="subcommand", title="subcommands", help="command to run"
)
subparsers.required = True

helps = {
    # Subcommands and options
    "play": "resume playback",
    "pause": "pause playback",
    "toggle": "switch between playing and paused states",
    "rewind": "return to the beginning of the current song",
    "ff": "jump to the end of the current song",
    "seek": "jump to a specific position in the current song",
    "timestamp": "position to jump to, [mm:]ss",
    "prev": "go to the beginning of the previous song",
    "next": "go to the beginning of the next song",
    "goto": "go to a specific numbered song in the play queue",
    "first": "go to the first song in the play queue",
    "last": "go to the last song in the play queue",
    "status": "display the current playback status",
    "inorder": "play songs in seqeuential order",
    "random": "play songs in random order, no constraints",
    "shuffle": "play songs in random order, but play all before repeating",
    "shufnew": "play songs in random order, no consecutive plays of the same song",
    "stop": "terminate playback after playing all songs",
    "loop": "start over after playing all songs",
    "loop1": "repeat only current song",
    "finish": "jump to up-next play queue",
    "erase": "delete contents of play queue or playlist",
    "replace": "replace contents of play queue or playlist with given song(s)",
    "prepend": "insert given song(s) at beginning of play queue or playlist",
    "append": "insert given song(s) at end of play queue or playlist",
    "insert": "insert given songs(s) in middle of play queue or playlist",
    "tofirst": "move songs to beginning of play queue or playlist",
    "tolast": "move songs to end of play queue or playlist",
    "remove": "delete songs from play queue or playlist",
    "randomize": "put play queue or playlist into random order",
    "upnext": "act on the up-next play queue instead of the primary play queue",
    # Arguments
    "obj": "the playlist, album, or song to add",
    "as": "disambiguate what kind of object the name refers to",
    "from": "disambiguate what album the song is from",
}

parser_play = subparsers.add_parser("play", help=helps["play"])
parser_pause = subparsers.add_parser("pause", help=helps["pause"])
parser_toggle = subparsers.add_parser("toggle", help=helps["toggle"])

parser_rewind = subparsers.add_parser("rewind", help=helps["rewind"])
parser_rewind.add_argument("amt", nargs="?", help="rewind by only this much, [mm:]ss")
parser_ff = subparsers.add_parser("ff", help=helps["ff"])
parser_ff.add_argument(
    "amt", nargs="?", help="fast-forward by only this much, [mm:]ss",
)
parser_seek = subparsers.add_parser("seek", help=helps["seek"])
parser_seek.add_argument("timestamp", help=helps["timestamp"])

parser_prev = subparsers.add_parser("prev", help=helps["prev"])
parser_prev.add_argument(
    "num",
    nargs="?",
    type=int,
    default=1,
    help="how many songs before the current one to go to",
)
parser_next = subparsers.add_parser("next", help=helps["next"])
parser_next.add_argument(
    "num",
    nargs="?",
    type=int,
    default=1,
    help="how many songs after the current one to go to",
)
parser_goto = subparsers.add_parser("goto", help=helps["goto"])
parser_goto.add_argument(
    "idx", type=int, help="the number of the song to go to (counting from one)"
)

parser_first = subparsers.add_parser("first", help=helps["first"])
parser_last = subparsers.add_parser("last", help=helps["last"])

parser_status = subparsers.add_parser("status", help=helps["status"])

for subparser in (
    parser_play,
    parser_pause,
    parser_toggle,
    parser_rewind,
    parser_ff,
    parser_seek,
    parser_prev,
    parser_next,
    parser_goto,
    parser_first,
    parser_last,
    parser_status,
):
    if subparser not in (parser_play, parser_pause):
        group = subparser.add_mutually_exclusive_group()
        group.add_argument(
            "--play",
            dest="play",
            action="store_const",
            const="play",
            help=helps["play"],
        )
        group.add_argument(
            "--pause",
            dest="play",
            action="store_const",
            const="pause",
            help=helps["pause"],
        )
        group.add_argument(
            "--toggle",
            dest="play",
            action="store_const",
            const="toggle",
            help=helps["toggle"],
        )
        group.set_defaults(play=None)
    if subparser not in (parser_rewind, parser_ff, parser_seek):
        group = subparser.add_mutually_exclusive_group()
        group.add_argument(
            "--rewind",
            dest="seek",
            action="store_const",
            const="rewind",
            help=helps["rewind"],
        )
        group.add_argument(
            "--ff", dest="seek", action="store_const", const="ff", help=helps["ff"]
        )
        group.add_argument(
            "--seek",
            dest="seek",
            action=StoreConstPlusAction,
            const="seek",
            val_dest="timestamp",
            help=helps["timestamp"],
        )
    if subparser not in (
        parser_prev,
        parser_next,
        parser_goto,
        parser_first,
        parser_last,
    ):
        group = subparser.add_mutually_exclusive_group()
        group.add_argument(
            "--prev",
            dest="goto",
            action="store_const",
            const="prev",
            help=helps["prev"],
        )
        group.add_argument(
            "--next",
            dest="goto",
            action="store_const",
            const="next",
            help=helps["next"],
        )
        group.add_argument(
            "--goto",
            dest="goto",
            action=StoreConstPlusAction,
            const="goto",
            val_dest="idx",
            help=helps["goto"],
        )
        group.add_argument(
            "--first",
            dest="goto",
            action="store_const",
            const="first",
            help=helps["first"],
        )
        group.add_argument(
            "--last",
            dest="goto",
            action="store_const",
            const="last",
            help=helps["last"],
        )
    if subparser != parser_status:
        subparser.add_argument("--status", action="store_true", help=helps["status"])

parser_inorder = subparsers.add_parser("inorder", help=helps["inorder"])
parser_random = subparsers.add_parser("random", help=helps["random"])
parser_shuffle = subparsers.add_parser("shuffle", help=helps["shuffle"])
parser_shufnew = subparsers.add_parser("shufnew", help=helps["shufnew"])

parser_stop = subparsers.add_parser("stop", help=helps["stop"])
parser_loop = subparsers.add_parser("loop", help=helps["loop"])
parser_loop1 = subparsers.add_parser("loop1", help=helps["loop1"])

parser_finish = subparsers.add_parser("finish", help=helps["finish"])

parser_erase = subparsers.add_parser("erase", help=helps["erase"])
parser_replace = subparsers.add_parser("replace", help=helps["replace"])
parser_replace.add_argument("obj", help=helps["obj"])

parser_prepend = subparsers.add_parser("prepend", help=helps["prepend"])
parser_prepend.add_argument("obj", help=helps["obj"])
parser_append = subparsers.add_parser("append", help=helps["append"])
parser_append.add_argument("obj", help=helps["obj"])
parser_insert = subparsers.add_parser("insert", help=helps["insert"])
parser_insert.add_argument(
    "idx",
    type=int,
    help="the number of the song before which to insert (counting from one)",
)
parser_insert.add_argument("obj", help=helps["obj"])

parser_tofirst = subparsers.add_parser("tofirst", help=helps["tofirst"])
parser_tofirst.add_argument(
    "idx",
    type=int,
    help="the number of the song (or first song) to relocate (counting from one)",
)
parser_tofirst.add_argument(
    "--to", type=int, help="the number of the last song to relocate (counting from one)"
)
parser_tolast = subparsers.add_parser("tolast", help=helps["tolast"])
parser_tolast.add_argument(
    "idx",
    type=int,
    help="the number of the song (or first song) to relocate (counting from one)",
)
parser_tolast.add_argument(
    "--to", type=int, help="the number of the last song to relocate (counting from one)"
)

parser_remove = subparsers.add_parser("remove", help=helps["remove"])
parser_remove.add_argument(
    "idx",
    type=int,
    help="the number of the song (or first song) to remove (counting from one)",
)
parser_remove.add_argument(
    "--to", type=int, help="the number of the last song to remove (counting from one)"
)

parser_randomize = subparsers.add_parser("randomize", help=helps["randomize"])

for subparser in (
    parser_inorder,
    parser_random,
    parser_shuffle,
    parser_shufnew,
    parser_stop,
    parser_loop,
    parser_loop1,
    parser_erase,
    parser_replace,
    parser_prepend,
    parser_append,
    parser_insert,
    parser_tofirst,
    parser_tolast,
    parser_remove,
    parser_randomize,
):
    if subparser not in (parser_inorder, parser_random, parser_shuffle, parser_shufnew):
        group = subparser.add_mutually_exclusive_group()
        group.add_argument(
            "--inorder",
            dest="order",
            action="store_const",
            const="inorder",
            help=helps["inorder"],
        )
        group.add_argument(
            "--random",
            dest="order",
            action="store_const",
            const="random",
            help=helps["random"],
        )
        group.add_argument(
            "--shuffle",
            dest="order",
            action="store_const",
            const="shuffle",
            help=helps["shuffle"],
        )
        group.add_argument(
            "--shufnew",
            dest="order",
            action="store_const",
            const="shufnew",
            help=helps["shufnew"],
        )
    if subparser not in (parser_stop, parser_loop, parser_loop1):
        group = subparser.add_mutually_exclusive_group()
        group.add_argument(
            "--stop",
            dest="order",
            action="store_const",
            const="stop",
            help=helps["stop"],
        )
        group.add_argument(
            "--loop",
            dest="order",
            action="store_const",
            const="loop",
            help=helps["loop"],
        )
        group.add_argument(
            "--loop1",
            dest="order",
            action="store_const",
            const="loop1",
            help=helps["loop1"],
        )
    subparser.add_argument("--upnext", action="store_true", help=helps["upnext"])
    if subparser != parser_finish:
        subparser.add_argument("--finish", action="store_true", help=helps["finish"])
    if subparser in (parser_replace, parser_prepend, parser_append, parser_insert):
        subparser.add_argument(
            "--as", choices=("playlist", "album", "song"), help=helps["as"]
        )
        subparser.add_argument("--from", metavar="ALBUM", help=helps["from"])
    if subparser in (
        parser_erase,
        parser_replace,
        parser_prepend,
        parser_append,
        parser_insert,
        parser_tofirst,
        parser_tolast,
        parser_remove,
        parser_randomize,
    ):
        subparser.add_argument(
            "--playlist", help="act on the given playlist instead of the play queue"
        )

parser_playlists = subparsers.add_parser(
    "playlists", help="list playlists from the library"
)
parser_playlists.add_argument("query", nargs="?", help="only show matching playlists")
parser_albums = subparsers.add_parser("albums", help="list albums from the library")
parser_albums.add_argument("query", nargs="?", help="only show matching albums")
parser_songs = subparsers.add_parser("songs", help="list songs from the library")
parser_songs.add_argument("query", nargs="?", help="only show matching songs")
parser_songs.add_argument(
    "--filter",
    metavar="KEY(=|~)VALUE,...",
    help="filter songs by metadata fields (~ for regexp)",
)
parser_songs.add_argument(
    "--sort",
    metavar="KEY[:(s|r|x)],...",
    help="sort songs by metadata fields (s = normal, r = reverse, x = random)",
)
parser_view = subparsers.add_parser("view", help="display album artwork")
parser_view.add_argument("obj", help="album or song")
parser_list = subparsers.add_parser("list", help="list songs in play queue")
group = parser_list.add_mutually_exclusive_group()
group.add_argument(
    "obj", nargs="?", help="album or playlist to list instead of play queue"
)
group.add_argument("--upnext", action="store_true", help="")
parser_list.add_argument("--as", choices=("playlist", "album"), help=helps["as"])

parser_show = subparsers.add_parser("show", help="inspect song metadata")
parser_show.add_argument("obj", help="playlist, album, or song")
parser_show.add_argument(
    "key", nargs="*", help="display detailed information for given keys"
)
parser_set = subparsers.add_parser("set", help="update song metadata")
parser_set.add_argument("obj", help="playlist, album, or song")
parser_set.add_argument(
    "key", metavar="KEY=VALUE", nargs="+", help="key and value to update",
)
parser_edit = subparsers.add_parser(
    "edit", help="edit song metadata in external editor"
)
parser_edit.add_argument("obj", help="playlist, album, or song")
parser_edit.add_argument(
    "key", nargs="*", help="perform advanced editing on given keys"
)

for subparser in (parser_show, parser_set, parser_edit):
    subparser.add_argument(
        "--as", choices=("playlist", "album", "song"), help=helps["as"]
    )
    subparser.add_argument("--from", metavar="ALBUM", help=helps["from"])

parser_log = subparsers.add_parser("log", help="display version-control history")
parser_revert = subparsers.add_parser(
    "revert", help="revert to previous version of library"
)
parser_revert.add_argument("hash", nargs="?", help="Git commit hash")

parser_help = subparsers.add_parser("help", help="display this message")
parser_restart = subparsers.add_parser(
    "restart", help="restart Pyrelight command server"
)

for flag in ("-?", "-help"):
    parser.add_argument(flag, dest="help", action="store_true", help=argparse.SUPPRESS)


def parse_cmdline(cmdline):
    global global_output
    global_output = ""
    try:
        args = parser.parse_args(cmdline)
        return (args, global_output)
    except ArgumentParserExit as e:
        return (e.status == 0, global_output)
