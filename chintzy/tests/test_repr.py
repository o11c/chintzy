import unittest

import chintzy

class ReprTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_rule(self):
        from chintzy.rules import Rule

        x = Rule('x')
        assert repr(x) == "<chintzy.rules.Rule('x') with 0 alts>"
        x.add_alt([])
        assert repr(x) == "<chintzy.rules.Rule('x') with 1 alts>"
        x.add_alt([])
        assert repr(x) == "<chintzy.rules.Rule('x') with 2 alts>"

    def test_grammar(self):
        from chintzy.rules import Grammar

        g = Grammar('z9000', 'squish',
'''
a:
    b
    c d
''')
        assert repr(g) == "chintzy.rules.Grammar('z9000', 'squish', <1 rules>)"
        g.load(
'''
e:
    f
''')
        assert repr(g) == "chintzy.rules.Grammar('z9000', 'squish', <2 rules>)"
