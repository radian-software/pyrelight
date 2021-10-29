# Pyrelight

Attempt #4 at a personal music library manager and media player.

## Abstractions

You have a music library which contains a number of albums. Each album
has a piece of album artwork, and also a number of songs. Each song
has a media file (in MP3 format) and some associated metadata. The
metadata is a flat key-value map whose keys and values are both
strings. However, a few keys have certain constraints on the allowable
values. There is a fixed schema which specifies the allowed keys as
well as their meanings. However, aside from the schema constraints,
metadata is arbitrary. You can have multiple songs which are identical
in metadata, except for title.

Albums, playlists, and songs (within an album) must have unique
normalized names.

You can have playlists. A playlist has a name and an ordered sequence
of songs, which are not necessarily unique.

You can play songs. When playing songs, there is an active play queue
which is an ordered list of songs. The play queue can be populated by
inserting the songs from an album or playlist, or it can be modified
by rearranging, adding, or deleting individual songs at any point. A
pointer is maintained for the currently playing song such that changes
do not affect the currently playing song unless that song is removed
from the playlist or moved to a different point.

Playback has more than one mode. By default, songs play sequentially
and playback terminates at the end of the play queue. You can enable
or disable shuffle mode at any time, which causes a random song to be
played after the current song is finished. Shuffle mode has options.
Whether the same song is allowed to play twice in a row is
configurable at any point. Also configurable is whether the entire
play queue must be exhausted before a song is repeated. You can enable
loop mode, which causes playback to start over once the play queue is
exhausted. This mode is implied by shuffle mode, unless the shuffle is
in the mode which requires the entire play queue to be exhausted
before a song is repeated.

Media and artwork files are automatically managed by Pyrelight, and
renamed appropriately as metadata is modified. Pyrelight metadata is
automatically embedded as ID3 in media files as it is updated. Changes
to metadata are version-controlled, and you can roll back a change.
This will revert filesystem renames and re-embed the old metadata as
ID3, but it will not necessarily return the media files to exactly the
state that they were in before the change. In general, Pyrelight does
not respect ID3 metadata as a source of truth except optionally during
import. There is a persistent history of which songs have been played,
how many times, and at what timestamps. This information is stored
separately from the metadata and media files, and is not
version-controlled.

## Implementation

A specific directory is designated as your Pyrelight library. Multiple
libraries are not supported. This directory is version-controlled
using Git. It contains several subdirectories and files:

* `music/<album>/<song>.mp3`: media files.
* `artwork/<album>.{png,jpg,...}`: artwork files.
* `metadata.json`: song metadata.
* `session.json`: the play queue, current position, and playback
  state.
* `history.json`: persistent song playback history.

The entry point to Pyrelight is a single command-line tool named
`plt`. This tool interacts with a persistent background daemon which
is automatically started as necessary. The daemon keeps all
information in memory, but writes it asynchronously back to disk on
every change. For this reason, reading the JSON files directly is an
acceptable method of manipulating a Pyrelight library. Writing the
JSON files is also acceptable, as Pyrelight tracks filesystem
modification times of administrative files and re-reads them as
needed. However, writing the JSON files during a Pyrelight operation
produces unspecified results. The only guarantee is that no file will
become corrupted unless it is modified by both the external tool and
by Pyrelight in the concurrent operation.

Communication between `plt` and the Pyrelight daemon is handled via a
UNIX domain socket. The command-line tool can be run in several modes:

* By providing a single command as arguments on the command line.
* As a REPL, where an interactive prompt is output and commands are
  read successively from stdin.
* As a command server, for noninteractive usage by a client such as
  `pyrelight.el`.

## State

* Playback: boolean, enabled or disabled. Whether playback is enabled
  is meaningful even if there is no song selected. It affects what
  will happen when a song becomes selected.
* Seek position: seconds/minutes into currently selected song. This
  only has a value when there is a selected song. If the selected song
  hasn't started playing, it's set to zero. Clamped to length of
  currently selected song.
* Play queue: ordered list of songs (references, not affected by
  metadata changes but still affected by song deletions). Can be
  empty.
* Up next queue: same as play queue.
* Queue index: pointer into play queue. Has a value if and only if the
  play queue is not empty. Clamped to bounds of play queue.

## Command interface

Commands are parsed using the standard GNU conventions. Input and
output are done via stdio if relevant to the given command. They may
be in JSON or another format.

Basic subcommands are as follows:

* Playback control
    * `play`: Enable playback.
    * `pause`: Disable playback.
    * `toggle`: Toggle playback between enabled and disabled.
    * `rewind [<amt>]`: Set seek position to beginning of song, or if
      `<amt>` is provided then backwards that many seconds/minutes
      from the current position. No effect if no selected song.
    * `ff [<amt>]`: Set seek position to end of song (actually,
      beginning of next song), or if `<amt>` is provided then forwards
      that many seconds/minutes from the current position. No effect
      if no selected song.
    * `seek <time>`: Set seek position directly.
* Play queue navigation
    * `prev [<num>]`: Go to beginning of previous song, or back
      `<num>` songs (default behavior corresponds to `<num>` of 1).
      Negative and zero `<num>` is allowed.
    * `next [<num>]`: Go to beginning of next song, or forwards
      `<num>` songs (default behavior corresponds to `<num>` of 1).
      Negative and zero `<num>` is allowed.
    * `goto <idx>`: Go to beginning of song at given index in play
      queue (indexed from 1).
    * `first`: Go to beginning of first song in play queue.
    * `last`: Go to beginning of last song in play queue.
    * `finish`: Go to ... FIXME

### Playback control

Commands:

```
play
pause
toggle

rewind [<amt>]
ff [<amt>]
seek <timestamp>

prev [<num>]
next [<num>]
goto <idx>

first
last
finish

status
```

Options:

```
--play
--pause

--rewind
--ff
--seek <timestamp>

--prev
--next
--goto <idx>

--first
--last
--finish

--status
```

### Sequence management

Commands:

```
inorder
random
shuffle
shufnew

stop
loop
loop1
```

Options:

```
--inorder
--random
--shuffle
--shufnew

--stop
--loop
--loop1

--upnext
```

### Play queue and playlist management

Objects can be albums, songs, or playlists (full names, automatically
normalized).

Commands:

```
erase
replace <obj>

prepend <obj>
append <obj>
insert <idx> <obj>

tofirst <idx> [--to <idx>]
tolast <idx> [--to <idx>]

remove <idx> [--to <idx>]

randomize

finalize
```

Options:

```
--as (playlist | album | song)
--from <album>

--playlist <playlist>
--upnext

--inorder
--random
--shuffle
--shufnew

--stop
--loop
--loop1

--finalize
```

### Query

Queries are processed with normalized substring matching.

Commands:

```
playlists [<query>]
albums [<query>]
songs [<query>]
view <album>
list [<playlist|album>]
```

Options for `playlists`, `albums`, and `songs`:

```
--filter <key>(=|==|~)<value>,...
--sort <key>[:(s|r|x)],...
```

Options for `list`:

```
--as (playlist | album)
--upnext
```

### Editing

Commands:

```
show <obj> [<key>...]
set <obj> <key>=<value>...
edit <obj> [<key>...]
```

Options:

```
--as (playlist | album | song)
--from <playlist>
```

### Version-control

Commands:

```
log
revert [<hash>]
```

### Administrative

```
down
help
```
