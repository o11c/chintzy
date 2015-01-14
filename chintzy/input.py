from __future__ import print_function, unicode_literals

from collections import namedtuple
import io

# can't use wcwidth because it doesn't handle combining characters
from wcwidth import wcswidth

Location = namedtuple('Location', ['index_in_file', 'nominal_line', 'index_in_line', 'nominal_column'])
Span = namedtuple('Span', ['begin', 'end'])

def tab(vcol):
    return vcol - ((vcol - 1) % 8) + 8

class InputSource(object):
    __slots__ = ('_filename', '_text', '_loc')

    def __init__(self, name, body=None):
        if body is None:
            # removes all \r in favor of \n
            # TODO try to understand what the standard requires
            # but even if it requires something different, chintzy
            # only intends to support "reasonable" programs.
            with io.open(name) as f: #pragma NO COVER
                body = f.read() #pragma NO COVER
        if not body.endswith('\n'):
            body += '\n'
        self._filename = name
        self._text = body
        self._loc = self.begin_location()

    def begin_location(self):
        return Location(0, 1, 0, 1)

    def adv(self):
        self._loc = self.calc_adv(self._loc)

    def calc_adv(self, loc):
        i, l, c, v = loc
        old_ch = self._text[i]
        i += 1
        #new_ch = self._text[i:i+1]
        c += 1
        # \r is removed earlier
        if old_ch == '\n':
            l += 1
            c = 0
            v = 1
        elif old_ch == '\t':
            v = tab(v)
        else:
            if old_ch == '\v' or old_ch == '\f':
                old_ch = ' '
            w = wcswidth(old_ch)
            assert w != -1, 'character %r has unknown size' % v
            v += w
        return Location(i, l, c, v)

    def get(self, loc=None):
        if loc is None:
            loc = self._loc
        i = loc.index_in_file
        return loc, self._text[i:i+1]

    def message_str(self, *args, **kwargs):
        s = io.StringIO()
        self.message(*args, file=s, **kwargs)
        return s.getvalue()

    def message(self, span, cat, mes, opt='always enabled', file=None):
        if file is None:
            file = sys.stderr #pragma NO COVER
        print('%s:%u:%u: %s: %s [%s]'
                % (self._filename, span.begin.nominal_line, span.begin.nominal_column, cat, mes, opt),
                file=file)
        i0 = span.begin.index_in_file - span.begin.index_in_line
        if span.begin.nominal_line != span.end.nominal_line:
            i1 = self._text.index('\n', i0)
        elif span.end.index_in_file == len(self._text):
            i1 = span.end.index_in_file
        else:
            i1 = self._text.index('\n', span.end.index_in_file)
        text = self._text[i0:i1].replace('\v', ' ').replace('\f', ' ')
        print(text, file=file)
        spaces = span.begin.nominal_column - 1
        if span.begin.nominal_line != span.end.nominal_line:
            squiggles = wcswidth(text[span.begin.index_in_line+1:])
            dots = ' ...'
        else:
            squiggles = span.end.nominal_column - span.begin.nominal_column
            dots = ''
        print(' ' * spaces, '^', '~' * squiggles, dots, sep='', file=file)

    def __iter__(self, one_more=False, loc=None):
        while True:
            l, c = self.get(loc)
            if not c:
                if one_more:
                    yield l, c
                break
            yield l, c
            if loc is None:
                self.adv()
            else:
                loc = self.calc_adv(loc)
