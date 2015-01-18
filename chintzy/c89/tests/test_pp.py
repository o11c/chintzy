import unittest

from chintzy.input import InputSource

from ..std import name
from .. import pp
from ..pp import PreprocessorLexer

class TestPp(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_lex_special(self):
        lex = PreprocessorLexer(InputSource('<string>', ''))
        assert lex.get()
        assert repr(lex) == "<chintzy.%s.pp.PreprocessorLexer at <string>:1:1, with token '\\n'>" % name
        assert repr(lex.get()) == "chintzy.%s.pp.PpNewLine(<Span 1:1 - 1:1>, '\\n')" % name
        lex.adv()
        assert not lex.get()
        assert repr(lex) == "<chintzy.%s.pp.PreprocessorLexer at <string>:2:1, with token ''>" % name
        assert repr(lex.get()) == "chintzy.%s.pp.PpEof(<Span 2:1 - 2:1>, '')" % name

        lex = PreprocessorLexer(InputSource('<string>', '#include <a">'))
        while lex.get()._text != '\n':
            t = lex.get()
            lex.adv()
        assert repr(t) == "chintzy.%s.pp.PpAngleHeaderName(<Span 1:10 - 1:13>, '<a\">')" % name

        lex = PreprocessorLexer(InputSource('<string>', 'b\n#include "c\\"'))
        while lex.get()._text != '\n':
            t = lex.get()
            lex.adv()
        lex.adv()
        while lex.get()._text != '\n':
            t = lex.get()
            lex.adv()
        assert repr(t) == 'chintzy.%s.pp.PpQuoteHeaderName(<Span 2:10 - 2:13>, \'"c\\\\"\')' % name

    def test_lex_ident(self):
        cases = []
        cases += [
            ('a', "PpIdentifier(<Span 1:1 - 1:1>, 'a')"),
            (' abc ', "PpIdentifier(<Span 1:2 - 1:4>, 'abc')"),
        ]
        self.do_cases(cases)

    def test_lex_number(self):
        cases = []
        cases += [
            ('12xf', "PpNumber(<Span 1:1 - 1:4>, '12xf')"),
            ('123f', "PpNumber(<Span 1:1 - 1:4>, '123f')"),
            ('1x23', "PpNumber(<Span 1:1 - 1:4>, '1x23')"),
            ('1e23', "PpNumber(<Span 1:1 - 1:4>, '1e23')"),
            ('1e+3', "PpNumber(<Span 1:1 - 1:4>, '1e+3')"),
            ('1E-3', "PpNumber(<Span 1:1 - 1:4>, '1E-3')"),
            ('.12e', "PpNumber(<Span 1:1 - 1:4>, '.12e')"),
            ('1.2e', "PpNumber(<Span 1:1 - 1:4>, '1.2e')"),
        ]
        self.do_cases(cases)

    if pp.pp_digit_separators:
        def test_lex_digitsep(self):
            cases = []
            cases += [
                ("1'2", "PpNumber(<Span 1:1 - 1:3>, \"1'2\")"),
                ("1'a", "PpNumber(<Span 1:1 - 1:3>, \"1'a\")"),
                ("1'_", "PpNumber(<Span 1:1 - 1:3>, \"1'_\")"),
            ]
            self.do_cases(cases)

    def test_lex_mlc(self):
        cases = []
        cases += [
            ('/***/', "PpComment(<Span 1:1 - 1:5>, '/***/')"),
            ('/*/*/', "PpComment(<Span 1:1 - 1:5>, '/*/*/')"),
            ('/*\\*/', "PpComment(<Span 1:1 - 1:5>, '/*\\\\*/')"),
            ('/* */', "PpComment(<Span 1:1 - 1:5>, '/* */')"),
            ('/**/', "PpComment(<Span 1:1 - 1:4>, '/**/')"),
        ]
        self.do_cases(cases)

    if name != 'c89':
        def test_lex_slc(self):
            cases = []
            cases += [
                ('//', "PpComment(<Span 1:1 - 1:2>, '//')"),
                ('// ', "PpComment(<Span 1:1 - 1:3>, '// ')"),
                ('//*', "PpComment(<Span 1:1 - 1:3>, '//*')"),
                ('//\\', "PpComment(<Span 1:1 - 1:2>, '//')"),
                ('//\\\n\n', "PpComment(<Span 1:1 - 1:2>, '//')"),
                ('//\\\na', "PpComment(<Span 1:1 - 2:1>, '//a')"),
            ]
            self.do_cases(cases)

    def test_lex_char(self):
        cases = []
        udls = ['']
        if pp.pp_has_udls:
            udls += ['_', 's', '_s', '_1']
        self.do_cases(cases)
        for p in pp.pp_char_prefix | {''}:
            for u in udls:
                for s in [
                    'abc',
                    '\\\'',
                    '\\"',
                    '\\?',
                    '\\\\',
                    '\\a',
                    '\\b',
                    '\\f',
                    '\\n',
                    '\\r',
                    '\\t',
                    '\\v',
                    '\\0',
                    '\\12',
                    '\\345',
                    '\\xa',
                    '\\xaB',
                    '\\xaBc',
                    '\\uaBcd',
                    '\\UaBcdef12',
                ]:
                    if not pp.pp_has_ucn and 'u' in s.lower():
                        continue
                    psu = "%s'%s'%s" % (p, s, u)
                    cases += [
                        (psu, 'PpChar(<Span 1:1 - 1:%d>, %s)' % (len(psu), repr(psu).lstrip('u'))),
                    ]
        self.do_cases(cases)

    def test_lex_str(self):
        cases = []
        udls = ['']
        if pp.pp_has_udls:
            udls += ['_', 's', '_s', '_1']
        self.do_cases(cases)
        for p in pp.pp_str_prefix | {''}:
            for u in udls:
                for s in [
                    'abc',
                    '\\\'',
                    '\\"',
                    '\\?',
                    '\\\\',
                    '\\a',
                    '\\b',
                    '\\f',
                    '\\n',
                    '\\r',
                    '\\t',
                    '\\v',
                    '\\0',
                    '\\12',
                    '\\345',
                    '\\xa',
                    '\\xaB',
                    '\\xaBc',
                    '\\uaBcd',
                    '\\UaBcdef12',
                ]:
                    if not pp.pp_has_ucn and 'u' in s.lower():
                        continue
                    psu = '%s"%s"%s' % (p, s, u)
                    cases += [
                        (psu, 'PpString(<Span 1:1 - 1:%d>, %s)' % (len(psu), repr(psu).lstrip('u'))),
                    ]
        self.do_cases(cases)

    def test_lex_str_raw(self):
        cases = []
        udls = ['']
        if pp.pp_has_udls:
            udls += ['_', 's', '_s', '_1']
        for p in pp.pp_str_raw_prefix:
            for u in udls:
                cases += [
                    (p + '"(aaa)"' + u, 'PpString(<Span 1:1 - 1:%d>, \'%s"(aaa)"%s\')' % (len(p) + 7 + len(u), p, u)),
                    (p + '"a(a)a"' + u, 'PpString(<Span 1:1 - 1:%d>, \'%s"a(a)a"%s\')' % (len(p) + 7 + len(u), p, u)),
                    (p + '"a\\(\\)a\\"' + u, 'PpString(<Span 1:1 - 1:%d>, \'%s"a\\\\(\\\\)a\\\\"%s\')' % (len(p) + 9 + len(u), p, u)),
                ]
        self.do_cases(cases)

    def test_lex_punctuation(self):
        cases = []
        for p in pp.all_punctuation:
            cases += [
                (p, 'PpPunctuation(<Span 1:1 - 1:%d>, \'%s\')' % (len(p), p)),
            ]
        self.do_cases(cases)

    def do_cases(self, cases):
        for i, r in cases:
            self.do_pplex_case(i, r)

    def do_pplex_case(self, i, r):
        lex = PreprocessorLexer(InputSource('<string>', i))
        assert repr(lex.get()) == 'chintzy.%s.pp.%s' % (name, r)
        lex.adv()
        assert lex.get()._text == '\n'
        lex.adv()
        assert not lex.get()
