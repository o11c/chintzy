import unittest

import chintzy


def do_import(name):
    mod = __import__(name)
    for bit in name.split('.')[1:]:
        mod = getattr(mod, bit)
    return mod

class DotsTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def do_test_dots(self, std):
        mod = do_import('chintzy.std.{std}'.format(std=std))
        for gn in chintzy.grammars:
            filename = 'data/{std}-{gram}.dot'.format(std=std, gram=gn)
            go = getattr(mod, gn)
            with open(filename, 'w') as out:
                go.to_dot(out)

    # generate test_c89, etc.
    for lang in chintzy.languages:
        vl = getattr(chintzy, lang + '_standards')
        for std in vl:
            exec('def test_dots_{std}(self):\n    self.do_test_dots("{std}")'.format(std=std))
