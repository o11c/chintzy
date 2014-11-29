def cut_prefix(word, prefix):
    if word.startswith(prefix):
        return word[len(prefix):]
    return word

def cut_suffix(word, suffix):
    if word.endswith(suffix):
        return word[:-len(suffix)]
    return word

class Grammar:
    __slots__ = ('std', 'name', 'txt', 'rules')

    def __init__(self, std, name, txt):
        self.std = std
        self.name = name
        self.txt = txt
        self.rules = {}
        self.load(txt)

    def __repr__(self):
        return 'chintzy.rules.Grammar(%r, %r, <%d rules>)' % (
                self.std,
                self.name,
                len(self.rules)
        )

    def to_dot(self, dot):
        def escape(s):
            return s.replace('\\', '\\\\').replace('"', '\\"')
        def node(ident, label):
            print('"%s"[label="%s"];' % (escape(ident), escape(label)), file=dot)
        def edge(id1, id2):
            print('"%s" -> "%s";' % (escape(id1), escape(id2)), file=dot)
        print('digraph {', file=dot)

        seen_x = set()

        for rulename, rule in sorted(self.rules.items()):
            label = cut_prefix(rulename, 'x-')
            node(rulename, label)
            seen_edges = set()
            singles = set()
            for alt in rule.alts:
                for e in alt:
                    e = cut_suffix(e, '_opt')
                    elabel = cut_prefix(e, 'x-').replace('$', '')
                    if len(e) == 1 and e.isalnum():
                        singles.add(e)
                        continue
                    if e in seen_edges:
                        continue
                    seen_edges.add(e)
                    if e not in self.rules:
                        if not is_known(e):
                            assert False, 'UNKNOWN in %s: %s -> %s' % (self.std, rulename, e)
                        e += '-x-from-' + rulename
                        node(e, elabel)
                    edge(rulename, e)
            if singles:
                if len(singles) <= 4:
                    for e in singles:
                        elabel = e
                        if e not in self.rules:
                            e += '-x-from-' + rulename
                            node(e, elabel)
                        edge(rulename, e)
                else:
                    edge(rulename, 'any of: ' + ''.join(sorted(singles)))
        print('}', file=dot)

    def load(self, s):
        s = s.split('\n')
        s = [l for l in s if l and not l.startswith('$')]

        rule = None
        one_of = False
        for l in s:
            if not l.startswith(' '):
                if rule is not None:
                    assert rule.alts, 'Missing rule body for: ' + rule.name
                one_of = False

                r, c = l.split(':')
                c = c.strip()
                if not c:
                    pass
                elif c == '$ONE OF':
                    one_of = True
                else:
                    assert False, 'Unknown modifier: ' + c
                rule = self.rules[r] = Rule(r)
            else:
                l = l.strip()
                if l.startswith('$'):
                    el = [l]
                    if l.startswith('$ANYTHING BUT'):
                        pass
                    elif l.startswith('$each'):
                        pass
                    elif l == '$\\n':
                        pass
                    elif l == '$(':
                        pass
                    elif l == '$other implementation-defined characters':
                        pass
                    elif l == '$any character except a ) followed by d-char-sequence and double quote':
                        pass
                    else:
                        assert False, 'warning: unknown special case: ' + l
                else:
                    el = l.split()
                if one_of:
                    for e in el:
                        rule.add_alt([e])
                else:
                    rule.add_alt(el)

def is_known(e):
    if '$' in e:
        return True
    if len(e) == 1:
        if e.isalnum() or e == '_':
            return True
    if e in '''
        \\
        '
        "
    '''.split():
        return True
    if e in '''
        {       }       [       ]       #       ##      (       )
        <:      :>      <%      %>      %:      %:%:    ;       :       ...
        new     delete  ?       ::      .       .*
        +       -       *       /       %       ^       &       |       ~
        !       =       <       >       +=      -=      *=      /=      %=
        ^=      &=      |=      <<      >>      >>=     <<=     ==      !=
        <=      >=      &&      ||      ++      --      ,       ->*     ->
    '''.split():
        return True

    # keywords (C++, C, operator names)
    if e in '''
        alignas
        alignof
        asm
        auto
        bool
        break
        case
        catch
        char
        char16_t
        char32_t
        class
        const
        constexpr
        const_cast

        continue
        decltype
        default
        delete
        do
        double
        dynamic_cast
        else
        enum
        explicit
        export
        extern
        false
        float
        for

        friend
        goto
        if
        inline
        int
        long
        mutable
        namespace
        new
        noexcept
        nullptr
        operator
        private
        protected
        public

        register
        reinterpret_cast
        return
        short
        signed
        sizeof
        static
        static_assert
        static_cast
        struct
        switch
        template
        this
        thread_local
        throw

        true
        try
        typedef
        typeid
        typename
        union
        unsigned
        using
        virtual
        void
        volatile
        wchar_t
        while

        _Alignas
        _Alignof
        _Atomic
        _Bool
        _Complex
        _Generic
        _Imaginary
        _Noreturn
        _Static_assert
        _Thread_local
        restrict

        and
        and_eq
        bitand
        bitor
        compl
        not
        not_eq
        or
        or_eq
        xor
        xor_eq
    '''.split():
        return True

    # preprocessor keywords
    if e in '''
        ifdef
        ifndef
        elif
        else
        endif
        include
        define
        line
        error
        pragma
        undef
    '''.split():
        return True

    # accessed across bounds; special context-dependent keywords
    if e in '''
        string-literal
        preprocessing-token
        enumeration-constant
        constant
        literal
        identifier
        identifier-list
        constant-expression

        final
        override
        ""
    '''.split():
        return True
    return False

class Rule:
    __slots__ = ('name', 'alts')

    def __init__(self, name):
        self.name = name
        self.alts = []

    def __repr__(self):
        return '<chintzy.rules.Rule(%r) with %d alts>' % (self.name, len(self.alts))

    def add_alt(self, alt):
        self.alts.append(list(alt))
