import unittest2
import sys

from twiggy import levels

class LevelTestCase(unittest2.TestCase):

    def test_display(self):
        assert str(levels.DEBUG) == 'DEBUG'
        assert repr(levels.DEBUG) == '<LogLevel DEBUG>'

    def test_name2level(self):
        assert levels.name2level('debug') is levels.DEBUG
        assert levels.name2level('Debug') is levels.DEBUG

    def test_less_than(self):
        assert levels.DEBUG < levels.INFO
        assert levels.INFO < levels.WARNING
        assert levels.WARNING < levels.ERROR
        assert levels.ERROR < levels.CRITICAL
        assert levels.CRITICAL < levels.DISABLED

    def test_greater_than(self):
        assert levels.INFO > levels.DEBUG
        assert levels.WARNING > levels.INFO
        assert levels.ERROR > levels.WARNING
        assert levels.CRITICAL > levels.ERROR
        assert levels.DISABLED > levels.CRITICAL


    def test_equality(self):
        assert levels.DEBUG == levels.DEBUG

    def test_bogus(self):
        assert levels.DEBUG != 1

        # XXX is there a comparable test for 2.x?
        if sys.version_info > (3,):
            with self.assertRaises(TypeError):
                levels.debug < 42
