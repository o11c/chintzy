import unittest

from .. import std

class TestDots(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_dots(self):
        import chintzy

        for gn in chintzy.grammars:
            filename = 'data/{std}-{gram}.dot'.format(std=std.name, gram=gn)
            go = getattr(std, gn)
            with open(filename, 'w') as out:
                go.to_dot(out)
