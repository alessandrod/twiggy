"""
Levels include (increasing severity): ``DEBUG``, ``INFO``, ``WARNING``, ``ERROR``, ``CRITICAL``, ``DISABLED``
"""

class LogLevel(object):
    """A log level. Users should *not* create new instances.

    Levels are opaque; they may be compared to each other, but nothing else.
    """

    __slots__ = ['__name', '__value']
    _name2levels = {}

    def __init__(self, name, value):
        self.__name = name
        self.__value = value
        self._name2levels[name] = self

    def __str__(self):
        return self.__name

    def __repr__(self):
        return "<LogLevel %s>"%self.__name

    def __lt__(self, other):
        if not isinstance(other, LogLevel):
            return NotImplemented
        else:
            return self.__value < other.__value

    def __eq__(self, other):
        if not isinstance(other, LogLevel):
            return NotImplemented
        else:
            return self.__value == other.__value

    def __hash__(self):
        return hash(self.__value) # pragma: no cover

def name2level(name):
    """return a `LogLevel` from a case-insensitve string"""
    return LogLevel._name2levels[name.upper()]

DEBUG = LogLevel('DEBUG', 1)
INFO = LogLevel('INFO', 2)
WARNING = LogLevel('WARNING', 3)
ERROR = LogLevel('ERROR', 4)
CRITICAL = LogLevel('CRITICAL', 5)
DISABLED = LogLevel('DISABLED', 6)
