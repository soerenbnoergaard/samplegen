import collections

sample_t = collections.namedtuple("sample_t", [
    "filename",
    "note_root",
    "note_max",
    "note_min",
    "loop_start",
    "loop_stop",
])

from . import bitwig
