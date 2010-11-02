import unittest

import re

from twiggy import filters, message, levels

from . import make_mesg

m = make_mesg()

class msgFilterTestCase(unittest.TestCase):

    # XXX more robust testing of the exact type/func.__name__ of the returned f
    # might be nice (instead of just callable), but eh.

    def test_None(self):
        f = filters.msgFilter(None)
        assert callable(f)
        assert f(m)

    def test_bool(self):
        f = filters.msgFilter(True)
        assert callable(f)
        assert f(m)

        f = filters.msgFilter(False)
        assert callable(f)
        assert not f(m)

    def test_basestring(self):
        f = filters.msgFilter("^Hello.*$")
        assert callable(f)
        assert f(m)

        f = filters.msgFilter("^Goodbye.*$")
        assert callable(f)
        assert not f(m)

    def test_regex(self):
        f = filters.msgFilter(re.compile("^Hello.*$"))
        assert callable(f)
        assert f(m)

        f = filters.msgFilter(re.compile("^Goodbye.*$"))
        assert callable(f)
        assert not f(m)

    def test_callable(self):
        my_func = lambda mesg: True
        f = filters.msgFilter(my_func)
        assert f is my_func

    def test_bad_arg(self):
        with self.assertRaises(ValueError):
            f = filters.msgFilter(42)


class namesTestCase(unittest.TestCase):

    def test_names(self):
        n = filters.names("foo", "bar")
        assert n.names == ("foo", "bar")

        assert filters.names("jose", "frank")(m)
        assert not filters.names("bob", "frank")(m)

    def test_glob_names(self):
        n = filters.glob_names("foo", "bar")
        assert n.names == ("foo", "bar")

        assert filters.glob_names("jo*", "frank")(m)
        assert not filters.glob_names("*bob", "frank")(m)

class EmitterTestCase(unittest.TestCase):

    def test_bad_min_level(self):
        with self.assertRaises(ValueError):
            filters.Emitter(42, None, None)

    def test_filter_property(self):
        # XXX we really should mock & test that msgFilter is being called. eh.

        e = filters.Emitter(levels.INFO, "^Hello.*$", 'output-unused')

        f = e.filter
        assert callable(f)
        assert f(m)

        e.filter = "^Goodbye.*$"
        f = e.filter
        assert callable(f)
        assert not f(m)
