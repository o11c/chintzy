import string

from ..input import Span
from ..phase2 import Phase2

from . import std

pp_ident1 = frozenset(string.ascii_letters + '_')
pp_digits = frozenset(string.digits)
pp_digits_or_dot = pp_digits | {'.'}
pp_identx = pp_ident1 | pp_digits
pp_white = frozenset(['\t', '\v', '\f', ' '])
pp_octal_digits = frozenset(string.octdigits)
pp_hex_digits = frozenset(string.hexdigits)


ppt_punc = {'operator', 'punctuator', 'preprocessing-op-or-punc'}
ppt_whitelist = ppt_punc | {'header-name', 'identifier', 'pp-number', 'character-constant', 'character-literal', 'user-defined-character-literal', 'string-literal', 'user-defined-string-literal', '$each non-white-space character that cannot be one of the above'}
preprocessing_token = std.lex.rules['preprocessing-token']
all_punctuation = set()
for (a,) in preprocessing_token.alts:
    assert a in ppt_whitelist
    if a in ppt_punc:
        pr = std.lex.rules[a]
        all_punctuation.update([x for (x,) in pr.alts])
del ppt_punc, ppt_whitelist
punctuation = set()
verbose_punctuation = set()
for p in all_punctuation:
    if pp_identx.issuperset(p):
        verbose_punctuation.add(p)
    else:
        punctuation.add(p)
for c in ['//', '/*']:
    assert c not in punctuation
    punctuation.add(c)
fake_punctuation = set()
for p in punctuation:
    for c in p:
        assert c in string.punctuation
    p_1 = p[:-1]
    if not p_1:
        continue
    if p_1 in punctuation:
        continue
    fake_punctuation.add(p_1)
    p_2 = p_1[:-1]
    assert p_2 in punctuation
del a, c, p, p_1, p_2
fake_punctuation.add('<::')
punctuation.update(fake_punctuation)
punctuation = frozenset(punctuation)
fake_punctuation = frozenset(fake_punctuation)
verbose_punctuation = frozenset(verbose_punctuation)

pp_num_exponents = {'e', 'E'}
# c99, c11
if ['pp-number', 'p', 'sign'] in std.lex.rules['pp-number'].alts:
    pp_num_exponents |= {'p', 'P'}
pp_num_exponents = frozenset(pp_num_exponents)

if ['pp-number', "'", 'digit'] in std.lex.rules['pp-number'].alts:
    pp_digit_separators = frozenset(["'"])
else:
    pp_digit_separators = frozenset()

pp_char_prefix = set()
pp_str_prefix = set()
pp_str_raw_prefix = set()
for a in (std.lex.rules.get('character-constant') or std.lex.rules['character-literal']).alts:
    a = ''.join(a)
    a = a.split("'")[0]
    if a:
        pp_char_prefix.add(a)
for a in (std.lex.rules.get('encoding-prefix') or std.lex.rules['string-literal']).alts:
    a = ''.join(a)
    a = a.split('"')[0]
    if a:
        pp_str_prefix.add(a)
    if 'raw-string' in std.lex.rules:
        pp_str_raw_prefix.add(a + 'R')
pp_char_prefix = frozenset(pp_char_prefix)
pp_str_prefix = frozenset(pp_str_prefix)
pp_str_raw_prefix = frozenset(pp_str_raw_prefix)

pp_simple_escapes = frozenset(x for bs, x in std.lex.rules['simple-escape-sequence'].alts)

pp_has_udls = 'user-defined-string-literal' in std.lex.rules
assert pp_has_udls == ('user-defined-character-literal' in std.lex.rules)

pp_has_ucn = 'universal-character-name' in std.lex.rules

class PpToken(object):
    __slots__ = ('_span', '_text')

    def __init__(self, span, text):
        self._span = span
        self._text = text

    def __repr__(self):
        return ('%s.%s(%r, %s)'
            % (
                self.__class__.__module__, self.__class__.__name__,
                self._span, repr(self._text).lstrip('u')
        ))

class PpEof(PpToken):
    __slots__ = ()

    def __bool__(self):
        return False
    __nonzero__ = __bool__

class PpHeaderName(PpToken):
    __slots__ = ()

class PpAngleHeaderName(PpHeaderName):
    __slots__ = ()

class PpQuoteHeaderName(PpHeaderName):
    __slots__ = ()

class PpIdentifier(PpToken):
    __slots__ = ()

class PpNumber(PpToken):
    __slots__ = ()

class PpChar(PpToken):
    __slots__ = ()

class PpString(PpToken):
    __slots__ = ()

class PpPunctuation(PpToken):
    __slots__ = ()

class PpComment(PpToken):
    __slots__ = ()

class PpNewLine(PpToken):
    __slots__ = ()


class PreprocessorLexer(object):
    __slots__ = ('_phase2', '_cur', '_header_name_phase')

    def __init__(self, src):
        self._phase2 = Phase2(src)
        # 0: nothing
        # 1: `new-line` (or start of file)
        # 2: `new-line`, `#`
        # 3: `new-line`, `#`, `include`
        self._header_name_phase = 1
        self.adv()

    def __repr__(self):
        return ('<chintzy.%s.pp.PreprocessorLexer at %s:%u:%u, with token %s>'
            % (
                std.name, self._phase2._src._filename,
                self._cur._span.begin.nominal_line, self._cur._span.begin.nominal_column,
                repr(self._cur._text).lstrip('u')
        ))


    def message(self, cur, cat, mes):               #pragma NO COVER
        span = Span(cur._begin, cur._end)           #pragma NO COVER
        self._phase2._src.message(span, cat, mes)   #pragma NO COVER

    def error(self, cur, mes):                      #pragma NO COVER
        self.message(cur, 'error', mes)             #pragma NO COVER

    def warning(self, cur, mes):                    #pragma NO COVER
        self.message(cur, 'warning', mes)           #pragma NO COVER

    def note(self, cur, mes):                       #pragma NO COVER
        self.message(cur, 'note', mes)              #pragma NO COVER

    def fatal(self, cur, mes):                      #pragma NO COVER
        self.error(cur, mes)                        #pragma NO COVER
        raise SystemExit                            #pragma NO COVER


    def get(self):
        return self._cur

    def adv(self):
        self._cur = self._calc_next()

    def _calc_next(self):
        # `header-name` would be ambiguous, don't use it normally, but
        # require it if previous tokens are [`#`, `include`] and the #
        # was not preceded by non-`new-line`.

        # `identifier` includes all keywords at this stage.
        # It is also convenient to include operators.

        # `pp-number` is overpermissive compared to later, and always
        # includes any suffixes.

        # `character-constant` is in c*, `character-literal` is in cxx*
        # `user-defined-character-literal` is in cxx11+
        # `string-literal` is blessedly common
        # `user-defined-string-literal` is in cxx11+
        # cxx11+ have raw string literals, which require undoing the
        # transformations in Phase2 and reading directly from
        # the InputSource, then resynchronizing the streams.

        # c89 has `operator` and `punctuation`, with overlap!
        # c99+ have it all in `punctuation`.
        # cxx* have it all in `preprocessing-op-or-punc`.
        # Canonicalize it all to `punctuation`, and remove identifiers.

        # TODO figure out what "each non-white-space character that
        # cannot be one of the above" covers.

        # Add `new-line` as its own token, it is not whitespace.
        # Note that lparen inspects the whitespace during parsing.

        # Note: most calls to _phase2.get() cannot return '',
        # because there is a guaranteed `\n` at the end.
        # The exceptions are:
        #   the initial whitespace skipper.
        #   the multi-line comment loop
        #   the raw string loop

        ph2 = self._phase2
        header_name_phase = self._header_name_phase
        self._header_name_phase = 0 # reset by default, set only if advance

        while True:
            tb = ph2.get()
            if not tb:
                return PpEof(*tb)
            if tb._buffer not in pp_white:
                break
            ph2.adv()

        if header_name_phase == 3:
            ph2.adv()
            if tb._buffer == '<':
                stop = '>'
                hnc = PpAngleHeaderName
            elif tb._buffer == '"':
                stop = '"'
                hnc = PpQuoteHeaderName
            else:
                self.fatal(tb, 'expected header name to start with < or "') #pragma NO COVER
            while True:
                tb2 = ph2.get()
                if tb2._buffer == '\n':
                    self.fatal(tb2, 'newline before end of header name') #pragma NO COVER
                tb += tb2
                ph2.adv()
                if tb2._buffer == stop:
                    return hnc(*tb)

        if tb._buffer == '\n':
            ph2.adv()
            self._header_name_phase = 1
            return PpNewLine(*tb)

        if tb._buffer in punctuation:
            while True:
                ph2.adv()
                tb2 = ph2.get()
                if tb2._buffer == '\n':
                    # Avoid an assertion error in TokenBuffer.__add__, if
                    # a file ends with backslash-newline (which will generate
                    # a new-line span on the same line instead of on a
                    # nonexistent line).
                    # TODO determine the most logical place to handle this.
                    break
                tbt = tb + tb2
                if tbt._buffer not in punctuation:
                    break
                tb = tbt
            if tb._buffer == '//':
                while True:
                    tb2 = ph2.get()
                    if tb2._buffer == '\n':
                        break
                    ph2.adv()
                    tb += tb2
                return PpComment(*tb)
            if tb._buffer == '/*':
                star = False
                while True:
                    tb2 = ph2.get()
                    if not tb2:
                        self.fatal('eof in multi-line comment') #pragma NO COVER
                    ph2.adv()
                    tb += tb2
                    if star and tb2._buffer == '/':
                        break
                    star = tb2._buffer == '*'
                return PpComment(*tb)
            if not (tb._buffer == '.' and tb2._buffer in pp_digits):
                if tb._buffer == '#' and header_name_phase == 1:
                    self._header_name_phase = 2
                if tb in fake_punctuation:
                    # there are three cases here currently:
                    # .. (needed for ..., should lex as . . instead)
                    # %:% (needed for %:%:, should lex as %: % instead)
                    # <:: (would normally be <: :, but should be < ::)
                    # TODO handle this later like template >> ?
                    # a true compiler can't because of token pasting
                    self.fatal(tb, 'sorry, unimplemented: early breaking of fake punctuation') #pragma NO COVER
                return PpPunctuation(*tb)
        if tb._buffer in pp_digits_or_dot:
            # dot is already advanced from the operator feeding
            if tb._buffer != '.':
                ph2.adv()
            while True:
                tb2 = ph2.get()
                if tb2._buffer in pp_digits_or_dot:
                    tb += tb2
                    ph2.adv()
                    continue
                if tb2._buffer in pp_num_exponents:
                    tb += tb2
                    ph2.adv()
                    tb2 = ph2.get()
                    if tb2._buffer in {'-', '+'}:
                        tb += tb2
                        ph2.adv()
                    continue #pragma NO COVER
                if tb2._buffer in pp_digit_separators:
                    tb += tb2
                    ph2.adv()
                    tb2 = ph2.get()
                    if not (tb2._buffer in pp_identx):
                        # TODO should be the start of a new character literal
                        # testcase: 1' '
                        # gcc 4.9 errors, bug 64626
                        # clang 3.4 accepts
                        self.fatal(tb2, 'sorry, unimplemented: digit separator not followed by a digit or nondigit') #pragma NO COVER
                    tb += tb2
                    ph2.adv()
                    continue
                if tb2._buffer in pp_ident1:
                    tb += tb2
                    ph2.adv()
                    continue
                break
            return PpNumber(*tb)

        if tb._buffer in pp_ident1:
            tb = self._lex_ident()
            tb2 = ph2.get()
            if tb._buffer in pp_char_prefix and tb2._buffer == "'":
                tb += self._lex_char()
                return PpChar(*tb)
            if tb._buffer in pp_str_prefix and tb2._buffer == '"':
                tb += self._lex_string()
                return PpString(*tb)
            if tb._buffer in pp_str_raw_prefix and tb2._buffer == '"':
                tb += self._lex_raw_string()
                return PpString(*tb)
            if tb._buffer in verbose_punctuation:
                return PpPunctuation(*tb)
            if header_name_phase == 2 and tb._buffer == 'include':
                self._header_name_phase = 3
            return PpIdentifier(*tb)
        if tb._buffer == "'":
            tb = self._lex_char()
            return PpChar(*tb)
        if tb._buffer == '"':
            tb = self._lex_string()
            return PpString(*tb)
        self.fatal(tb, 'no token starts with this') #pragma NO COVER

    def _lex_ident(self):
        ph2 = self._phase2
        tb = ph2.get()
        if tb._buffer not in pp_ident1:
            self.fatal(tb, 'bad ident start') #pragma NO COVER
        ph2.adv()
        while True:
            tb2 = ph2.get()
            if tb2._buffer not in pp_identx:
                break
            tb += tb2
            ph2.adv()
        return tb

    def _lex_char_or_string(self, quote):
        ph2 = self._phase2
        tb = ph2.get()
        ph2.adv()
        assert tb._buffer == quote
        while True:
            tb2 = ph2.get()
            tb += tb2
            ph2.adv()
            if tb2._buffer == quote:
                break
            if tb2._buffer == '\\':
                tb2 = ph2.get()
                if tb2._buffer in pp_simple_escapes:
                    tb += tb2
                    ph2.adv()
                    continue
                if tb2._buffer in pp_octal_digits:
                    tb += tb2
                    ph2.adv()
                    tb2 = ph2.get()
                    if tb2._buffer in pp_octal_digits:
                        tb += tb2
                        ph2.adv()
                        tb2 = ph2.get()
                        if tb2._buffer in pp_octal_digits:
                            tb += tb2
                            ph2.adv()
                    continue
                if tb2._buffer == 'x':
                    tb += tb2
                    ph2.adv()
                    tb2 = ph2.get()
                    if tb2._buffer not in pp_hex_digits:
                        self.fatal(tb2, 'not hex digit right after \\x') #pragma NO COVER
                    tb += tb2
                    ph2.adv()
                    while True:
                        tb2 = ph2.get()
                        if tb2._buffer not in pp_hex_digits:
                            break
                        tb += tb2
                        ph2.adv()
                    continue
                if pp_has_ucn:
                    if tb2._buffer == 'u':
                        tb += tb2
                        ph2.adv()
                        for _ in range(4):
                            tb2 = ph2.get()
                            if tb2._buffer not in pp_hex_digits:
                                self.fatal(tb2, 'not hex digit sometime after \\u') #pragma NO COVER
                            tb += tb2
                            ph2.adv()
                        continue
                    if tb2._buffer == 'U':
                        tb += tb2
                        ph2.adv()
                        for _ in range(8):
                            tb2 = ph2.get()
                            if tb2._buffer not in pp_hex_digits:
                                self.fatal(tb2, 'not hex digit sometime after \\U') #pragma NO COVER
                            tb += tb2
                            ph2.adv()
                        continue
                self.fatal(tb2, 'unknown escape') #pragma NO COVER
        if pp_has_udls and ph2.get()._buffer in pp_ident1:
            tb += self._lex_ident()
        return tb

    def _lex_char(self):
        return self._lex_char_or_string("'")

    def _lex_string(self):
        return self._lex_char_or_string('"')

    def _lex_raw_string(self):
        # " ddd ( rrr ) ddd "
        ph2 = self._phase2

        tb = ph2.get()
        assert tb._buffer == '"'
        ph2.adv_raw()

        while True:
            tb2 = ph2.get()
            tb += tb2
            ph2.adv_raw()
            if tb2._buffer == '(':
                break
        d = tb._buffer[1:-1]
        d = ')' + d
        if len(d) > 16:
            self.fatal(tb, 'raw string delimiter too long') #pragma NO COVER

        while True:
            tb2 = ph2.get()
            tb += tb2
            ph2.adv_raw()
            if tb._buffer.endswith(d) and ph2.get()._buffer == '"':
                break
        tb += ph2.get()
        ph2.adv()
        if pp_has_udls and ph2.get()._buffer in pp_ident1:
            tb += self._lex_ident()
        return tb
