import collections
import os
from collections.abc import Iterable


def _iterable(obj):
    return isinstance(obj, Iterable)


def _string(value):
    return isinstance(value, str)


def get(input):
    """return a list with input values or [] if input is None"""
    if input is None:
        return []
    if not _iterable(input) or _string(input):
        return [input]
    return list(input)


def _fullpath(path):
    return os.path.abspath(os.path.expanduser(path))


def _mkdir(path):
    if path.find("/") > 0 and not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))


def _utime(path):
    try:
        os.utime(path, None)
    except Exception:
        open(path, "a").close()


def touch(path):
    """mkdir + touch path(s)"""
    for path in get(path):
        if path:
            path = _fullpath(path)
            _mkdir(path)
            _utime(path)


touch("~/Desktop/_.xx")
