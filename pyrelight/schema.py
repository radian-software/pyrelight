import datetime
import decimal
import re


def boolean_validator(val):
    return val in ("yes", "no")


def date_validator(val):
    try:
        datetime.datetime.strptime(val, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def numeric_validator(val):
    return val == "0" or re.fullmatch(r"[1-9][0-9]*", val)


def usd_validator(val):
    parts = val.split(".")
    if len(parts) != 2:
        return False
    dollars, cents = parts
    return numeric_validator(dollars) and re.fullmatch(r"[0-9]{2}", cents)


def standard_sort_key(val):
    if not val:
        return (1,)
    else:
        return (0, val)


def numeric_sort_key(val):
    if not val:
        return (1,)
    else:
        return (0, int(val))


def usd_sort_key(val):
    if not val:
        return (1,)
    else:
        return (0, decimal.Decimal(val))


def year_validator(val):
    return re.fullmatch(r"[12][0-9]{3}", val)


SCHEMA = {}

for key in ("acquired_illegally", "acquired_legally", "as_bundle", "as_gift"):
    SCHEMA[key] = {
        "readonly": False,
        "validator": boolean_validator,
        "sort_key": standard_sort_key,
        "mandatory": True,
    }

for key in ("album", "album_artist", "artist", "title", "source"):
    SCHEMA[key] = {
        "readonly": False,
        "validator": None,
        "sort_key": standard_sort_key,
        "mandatory": True,
    }

for key in ("composer", "group", "refined_source", "tracklist"):
    SCHEMA[key] = {
        "readonly": False,
        "validator": None,
        "sort_key": standard_sort_key,
        "mandatory": False,
    }

for key in ("date",):
    SCHEMA[key] = {
        "readonly": False,
        "validator": date_validator,
        "sort_key": standard_sort_key,
        "mandatory": True,
    }

for key in ("disc", "track"):
    SCHEMA[key] = {
        "readonly": False,
        "validator": numeric_validator,
        "sort_key": numeric_sort_key,
        "mandatory": True,
    }

for key in ("id",):
    SCHEMA[key] = {
        "readonly": True,
        "sort_key": standard_sort_key,
        "mandatory": True,
    }

for key in (
    "min_price",
    "paid",
):
    SCHEMA[key] = {
        "readonly": False,
        "validator": usd_validator,
        "sort_key": usd_sort_key,
        "mandatory": True,
    }

for key in ("year",):
    SCHEMA[key] = {
        "readonly": False,
        "validator": year_validator,
        "sort_key": standard_sort_key,
        "mandatory": True,
    }
