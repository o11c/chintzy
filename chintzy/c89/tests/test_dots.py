import unittest

import chintzy
from .. import std

class TestDots(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def do_gn(self, gn):
        filename = 'data/{std}-{gram}.dot'.format(std=std.name, gram=gn)
        go = getattr(std, gn)
        with open(filename, 'w') as out:
            go.to_dot(out)

    for gn in chintzy.grammars:
        exec('''def test_dot_{gn}(self):
            self.do_gn('{gn}')'''.format(gn=gn))
