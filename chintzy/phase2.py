# coding=utf-8

from .py23 import *
from .input import InputSource, Span

class TokenBuffer(object):
    __slots__ = ('_begin', '_end', '_buffer')

    def __init__(self, begin, end, buf):
        self._begin = begin
        self._end = end
        self._buffer = unicode() + buf

    def __repr__(self):
        return ('chintzy.phase2.TokenBuffer(%r, %s)'
            % (
                Span(self._begin, self._end),
                repr(self._buffer).lstrip('u')
        ))

    def __iadd__(self, tb):
        assert (self._end.index_in_file + 1 == tb._begin.index_in_file
            or (self._end.index_in_file < tb._begin.index_in_file
                and tb._begin.index_in_line == 0))
        self._end = tb._end
        self._buffer += tb._buffer
        return self

    def __add__(self, tc):
        rv = TokenBuffer(self._begin, self._end, self._buffer)
        rv += tc
        return rv

    def __iter__(self):
        yield Span(self._begin, self._end)
        yield unicode(self._buffer)

    def __bool__(self):
        return bool(self._buffer)
    __nonzero__ = __bool__

class Phase2(object):
    __slots__ = ('_src', '_cur')

    trigraphs = {
        '??=': '#',
        '??/': '\\',
        '??\'': '^',
        '??(': '[',
        '??)': ']',
        '??!': '|',
        '??<': '{',
        '??>': '}',
        '??-': '~',
    }

    def __init__(self, src):
        assert isinstance(src, InputSource)
        self._src = src
        self.adv()

    def __repr__(self):
        return ('<chintzy.phase2.Phase2 at %s:%u:%u, forming %s>'
            % (
                self._src._filename,
                self._cur._begin.nominal_line, self._cur._begin.nominal_column,
                repr(self._cur._buffer).lstrip('u')
                # Note, python2 will also produce \u00e1 instead of á.
                # This is sad but I don't care enough to find a solution.
        ))

    # Does not handle trigraphs or backslash-newline, but screw them.
    def peek_harder(self):
        return self._src.get(offset=0)[1]

    def get(self):
        return self._cur

    def adv(self):
        self._cur = self._calc_next()

    def adv_raw(self):
        self._cur = self._calc_next_raw()

    def _calc_next(self):
        # loop just for backslash-newline's `continue`
        while True:
            l, c = self._src.get()
            if c == '':
                return TokenBuffer(l, l, c)
            self._src.adv()
            l2 = l
            if c == '?':
                _, c2 = self._src.get(offset=0)
                _, c3 = self._src.get(offset=1)
                tri = c + c2 + c3
                tri = Phase2.trigraphs.get(tri, None)
                if tri is not None:
                    self._src.adv()
                    l2, _ = self._src.get()
                    self._src.adv()
                    c = tri
            if c == '\\':
                _, n = self._src.get(offset=0)
                if n == '\n':
                    # Ensure file always ends with a newline.
                    # Technically, the position should still advance,
                    # but that would require mutating the text,
                    # and who cares that much about precise errors anyway,
                    # especially when it's not a "reasonable program"?
                    if l2.index_in_file + 2 != len(self._src._text):
                        self._src.adv()
                    continue #pragma NO COVER
            break
        return TokenBuffer(l, l2, c)

    def _calc_next_raw(self):
        l, c = self._src.get()
        if c != '':
            self._src.adv()
        return TokenBuffer(l, l, c)

    def iter(self, one_more=False):
        while True:
            tb = self.get()
            if not tb:
                if one_more:
                    yield tb
                break
            yield tb
            self.adv()
