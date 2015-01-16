from __future__ import unicode_literals

import unittest

import chintzy
from chintzy.input import (
        InputSource,
        Location,
        Span,
)


class TestInput(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_iter(self):
        i = InputSource('<string>', 'a')
        assert ''.join(c for _, c in i.iter(loc=i.begin_location())) == 'a\n'
        assert ''.join(c for _, c in i.iter()) == 'a\n'
        assert ''.join(c for _, c in i.iter()) == ''
        assert ''.join(c for _, c in i.iter(loc=i.begin_location())) == 'a\n'
        assert ''.join(c for _, c in i.iter()) == ''

    def test_location(self):
        i = InputSource('<string>', 'a\n')

        l, c = i.get()
        assert l.index_in_file == 0
        assert l.nominal_line == 1
        assert l.index_in_line == 0
        assert l.nominal_column == 1
        assert c == 'a'
        i.adv()

        l, c = i.get()
        assert l.index_in_file == 1
        assert l.nominal_line == 1
        assert l.index_in_line == 1
        assert l.nominal_column == 2
        assert c == '\n'
        i.adv()

        l, c = i.get()
        assert l.index_in_file == 2
        assert l.nominal_line == 2
        assert l.index_in_line == 0
        assert l.nominal_column == 1
        assert c == ''

    def test_span(self):
        src = InputSource('<string>', 'abcd\nefg\nhi\nj\n')

        (
            (a, _), (b, _), (c, _), (d, _), (n1, _),
            (e, _), (f, _), (g, _), (n2, _),
            (h, _), (i, _), (n3, _),
            (j, _), (n4, _),
            (x, _),
        ) = src.iter(one_more=True)

        assert (src.message_str(Span(a, a), 'error', 'the sky is falling', '-Wchicken') ==
'''<string>:1:1: error: the sky is falling [-Wchicken]
abcd
^
''')
        assert (src.message_str(Span(a, b), 'error', 'the sky is falling', '-Wchicken') ==
'''<string>:1:1: error: the sky is falling [-Wchicken]
abcd
^~
''')
        assert (src.message_str(Span(a, c), 'error', 'the sky is falling', '-Wchicken') ==
'''<string>:1:1: error: the sky is falling [-Wchicken]
abcd
^~~
''')
        assert (src.message_str(Span(a, d), 'error', 'the sky is falling', '-Wchicken') ==
'''<string>:1:1: error: the sky is falling [-Wchicken]
abcd
^~~~
''')
        assert (src.message_str(Span(a, n1), 'error', 'the sky is falling', '-Wchicken') ==
'''<string>:1:1: error: the sky is falling [-Wchicken]
abcd
^~~~~
''')
        assert (src.message_str(Span(a, e), 'error', 'the sky is falling', '-Wchicken') ==
'''<string>:1:1: error: the sky is falling [-Wchicken]
abcd
^~~~ ...
''')

        assert (src.message_str(Span(b, b), 'error', 'the sky is falling', '-Wchicken') ==
'''<string>:1:2: error: the sky is falling [-Wchicken]
abcd
 ^
''')
        assert (src.message_str(Span(b, c), 'error', 'the sky is falling', '-Wchicken') ==
'''<string>:1:2: error: the sky is falling [-Wchicken]
abcd
 ^~
''')
        assert (src.message_str(Span(b, d), 'error', 'the sky is falling', '-Wchicken') ==
'''<string>:1:2: error: the sky is falling [-Wchicken]
abcd
 ^~~
''')
        assert (src.message_str(Span(b, n1), 'error', 'the sky is falling', '-Wchicken') ==
'''<string>:1:2: error: the sky is falling [-Wchicken]
abcd
 ^~~~
''')
        assert (src.message_str(Span(b, e), 'error', 'the sky is falling', '-Wchicken') ==
'''<string>:1:2: error: the sky is falling [-Wchicken]
abcd
 ^~~ ...
''')

        assert (src.message_str(Span(c, d), 'error', 'the sky is falling', '-Wchicken') ==
'''<string>:1:3: error: the sky is falling [-Wchicken]
abcd
  ^~
''')
        assert (src.message_str(Span(c, n1), 'error', 'the sky is falling', '-Wchicken') ==
'''<string>:1:3: error: the sky is falling [-Wchicken]
abcd
  ^~~
''')
        assert (src.message_str(Span(c, e), 'error', 'the sky is falling', '-Wchicken') ==
'''<string>:1:3: error: the sky is falling [-Wchicken]
abcd
  ^~ ...
''')

        assert (src.message_str(Span(d, d), 'error', 'the sky is falling', '-Wchicken') ==
'''<string>:1:4: error: the sky is falling [-Wchicken]
abcd
   ^
''')
        assert (src.message_str(Span(d, n1), 'error', 'the sky is falling', '-Wchicken') ==
'''<string>:1:4: error: the sky is falling [-Wchicken]
abcd
   ^~
''')
        assert (src.message_str(Span(d, e), 'error', 'the sky is falling', '-Wchicken') ==
'''<string>:1:4: error: the sky is falling [-Wchicken]
abcd
   ^ ...
''')

        assert (src.message_str(Span(n1, n1), 'error', 'the sky is falling', '-Wchicken') ==
'''<string>:1:5: error: the sky is falling [-Wchicken]
abcd
    ^
''')
        assert (src.message_str(Span(n1, e), 'error', 'the sky is falling', '-Wchicken') ==
'''<string>:1:5: error: the sky is falling [-Wchicken]
abcd
    ^ ...
''')
        assert (src.message_str(Span(n1, f), 'error', 'the sky is falling', '-Wchicken') ==
'''<string>:1:5: error: the sky is falling [-Wchicken]
abcd
    ^ ...
''')

        assert (src.message_str(Span(h, i), 'error', 'the sky is falling', '-Wchicken') ==
'''<string>:3:1: error: the sky is falling [-Wchicken]
hi
^~
''')

        assert (src.message_str(Span(j, j), 'error', 'the sky is falling', '-Wchicken') ==
'''<string>:4:1: error: the sky is falling [-Wchicken]
j
^
''')
        assert (src.message_str(Span(j, n4), 'error', 'the sky is falling', '-Wchicken') ==
'''<string>:4:1: error: the sky is falling [-Wchicken]
j
^~
''')
        assert (src.message_str(Span(j, x), 'error', 'the sky is falling', '-Wchicken') ==
'''<string>:4:1: error: the sky is falling [-Wchicken]
j
^ ...
''')

        assert (src.message_str(Span(n4, n4), 'error', 'the sky is falling', '-Wchicken') ==
'''<string>:4:2: error: the sky is falling [-Wchicken]
j
 ^
''')
        assert (src.message_str(Span(n4, x), 'error', 'the sky is falling', '-Wchicken') ==
'''<string>:4:2: error: the sky is falling [-Wchicken]
j
 ^ ...
''')

        assert (src.message_str(Span(x, x), 'error', 'the sky is falling', '-Wchicken') ==
'''<string>:5:1: error: the sky is falling [-Wchicken]

^
''')

    def test_width(self):
        for src, width in [
            ('', 0),
            ('\uff20', 2),
            ('a\u0300', 1),
            ('\v', 1),
            ('\f', 1),
            ('\v\f', 2),
            ('\f\v', 2),
            ('\t', 8),
            ('a\t', 8),
            ('ab\t', 8),
            ('abc\t', 8),
            ('abcd\t', 8),
            ('abcde\t', 8),
            ('abcdef\t', 8),
            ('abcdefg\t', 8),
            ('abcdefgh\t', 16),
            ('abcdefg\u0300\t', 8),
            ('a\uff20\uff20\uff20\t', 8),
            ('aa\uff20\uff20\uff20\t', 16),
        ]:
            src = InputSource('<string>', src)
            for (x, _) in src.iter():
                pass
            assert x.nominal_column == width + 1

    def test_unprintable(self):
        src = InputSource('<string>', 'a\v \fb')
        for x, c in src.iter():
            if c == 'a':
                a = x
            elif c == 'b':
                b = x
        assert (src.message_str(Span(a, b), 'error', 'the sky is falling', '-Wchicken') ==
'''<string>:1:1: error: the sky is falling [-Wchicken]
a   b
^~~~~
''')
