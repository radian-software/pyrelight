import random
import re

from unidecode import unidecode

from pyrelight import LogicError, PyrelightError
from pyrelight.schema import SCHEMA


def normalize(val):
    return re.sub(r"[^a-z0-9]", "", unidecode(val).lower())


def create_matcher(filters):
    parsed_filters = []
    for filt in filters:
        for subfilter in filt.split(","):
            match = re.fullmatch(r"([^=~]+)(==|=|~)(.*)", subfilter)
            if not match:
                raise PyrelightError(f"malformed filter: {filt}")
            key, op, value = match.groups()
            if key not in SCHEMA:
                raise PyrelightError(f"unsupported key: {key}")
            if op == "=":
                value = normalize(value)
            parsed_filters.append((key, op, value))

    def matcher(song):
        for key, op, value in parsed_filters:
            song_value = song.get(key, "")
            if op == "==":
                matched = value == song_value
            elif op == "=":
                matched = value == normalize(song_value)
            elif op == "~":
                try:
                    matched = re.fullmatch(value, song_value)
                except re.error:
                    raise PyrelightError(f"invalid regex")
            else:
                raise LogicError(f"unexpected filter op: {op}")
            if not matched:
                return False
        return True

    return matcher


def sort_songlikes(songs, sorts):
    parsed_sorts = []
    for sort in sorts:
        for subsort in sort.split(","):
            match = re.fullmatch(r"([^:]+)(?::([a-zA-Z]))?", subsort)
            if not match:
                raise PyrelightError(f"malformed sort: {sort}")
            key, flag = match.groups()
            if not flag:
                flag = "s"
            if flag not in "srx":
                raise PyrelightError(f"unsupported sort flag: {sort}")


def playlist_to_song(playlist):
    return playlist[0]


def album_to_song(album):
    return album[min(album)]


def query_songs(metadata, *, filters, sorts):
    matcher = create_matcher(filters)
    matched_songs = {}
    for song_id, song in metadata["songs"].values():
        if matcher(song):
            matched_songs[song_id] = song
    return matched_songs


def query_albums(metadata, *, filters, sorts):
    matcher = create_matcher(filters)
    matched_albums = {}
    for album_name, album in metadata["albums"].items():
        if matcher(album_to_song(album)):
            matched_albums[album_name] = album
    return matched_albums


def query_playlists(metadata, *, filters, sorts):
    matcher = create_matcher(filters)
    matched_playlists = {}
    for playlist_name, playlist in metadata["playlists"].items():
        if matcher(playlist_to_song(playlist)):
            matched_playlists[playlist_name] = playlist
    return matched_playlists
