import argparse


class StoreConstPlusAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, val_dest=None, **kwargs):
        self.val_dest = val_dest if val_dest is not None else dest
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, self.const)
        setattr(namespace, self.val_dest, values)


parser = argparse.ArgumentParser(
    prog="plt", description="Fast command-line music library manager and media player.",
)
subparsers = parser.add_subparsers(dest="command", help="command to run")
subparsers.required = True

helps = {
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
