import unittest

class TestRepr(unittest.TestCase):

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

    def test_input(self):
        from chintzy.input import InputSource, Span
        i = InputSource('<string>', 'abc')
        assert repr(i) == '<chintzy.input.InputSource at <string>:1:1, codepoint 0/4>'
        l1, _ = i.get()
        i.adv()
        assert repr(i) == '<chintzy.input.InputSource at <string>:1:2, codepoint 1/4>'
        i.adv()
        assert repr(i) == '<chintzy.input.InputSource at <string>:1:3, codepoint 2/4>'
        i.adv()
        assert repr(i) == '<chintzy.input.InputSource at <string>:1:4, codepoint 3/4>'
        l2, _ = i.get()
        i.adv()
        assert repr(i) == '<chintzy.input.InputSource at <string>:2:1, codepoint 4/4>'
        l3, _ = i.get()

        s1 = Span(l1, l2)
        s2 = Span(l2, l3)
        assert repr(s1) == '<Span 1:1 - 1:4>'
        assert repr(s2) == '<Span 1:4 - 2:1>'

    def test_phase2(self):
        from chintzy.input import InputSource
        from chintzy.phase2 import Phase2
        p2 = Phase2(InputSource('<string>', 'abc'))
        assert repr(p2) == "<chintzy.phase2.Phase2 at <string>:1:1, forming 'a'>"
        p2.adv()
        assert repr(p2) == "<chintzy.phase2.Phase2 at <string>:1:2, forming 'b'>"
        p2.adv()
        assert repr(p2) == "<chintzy.phase2.Phase2 at <string>:1:3, forming 'c'>"
        p2.adv()
        assert repr(p2) == "<chintzy.phase2.Phase2 at <string>:1:4, forming '\\n'>"
        p2.adv()
        assert repr(p2) == "<chintzy.phase2.Phase2 at <string>:2:1, forming ''>"
