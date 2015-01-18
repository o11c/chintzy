# notes about parsing
# no implicit whitespace within a token, ever
# implicit whitespace within parse and pp trees usually
#
# bits of a rule are separated by whitespace
# terminals are single digits
# foo_opt is an implicit rule expanding to (foo | nothing)
#
# keywords are not explicitly excluded from identifiers
# "all but" rules in preprocessing-token c-char s-char h-char q-char
# lparen in function-like macro defines
#
# lex >> as two tokens of different types, generate > and >> in parser
# lex "" as its own thing and convert to string-literal in the parser
# lex 0 as its own token, add a -> integer-literal case in the parser
#
# since $ is invalid, use it as an escape of sorts (also section markers)

from ..rules import Grammar

# Annex A: Grammar summary

lex = Grammar('cxx11', 'lex', r'''
$2.12 Keywords, Table 4 & 5
$ override and final are special
x-keyword:   $ONE OF
    alignas     continue        friend      register            true
    alignof     decltype        goto        reinterpret_cast    try
    asm         default         if          return              typedef
    auto        delete          inline      short               typeid
    bool        do              int         signed              typename
    break       double          long        sizeof              union
    case        dynamic_cast    mutable     static              unsigned
    catch       else            namespace   static_assert       using
    char        enum            new         static_cast         virtual
    char16_t    explicit        noexcept    struct              void
    char32_t    export          nullptr     switch              volatile
    class       extern          operator    template            wchar_t
    const       false           private     this                while
    constexpr   float           protected   thread_local
    const_cast  for             public      throw

    and     and_eq  bitand  bitor   compl   not
    not_eq  or      or_eq   xor     xor_eq


$A.2 Lexical conventions
hex-quad:
    hexadecimal-digit hexadecimal-digit hexadecimal-digit hexadecimal-digit

universal-character-name:
    \ u hex-quad
    \ U hex-quad hex-quad

preprocessing-token:
    header-name
    identifier
    pp-number
    character-literal
    user-defined-character-literal
    string-literal
    user-defined-string-literal
    preprocessing-op-or-punc
    $each non-white-space character that cannot be one of the above

token:
    identifier
    x-keyword
    literal
    x-operator
    x-punctuator

header-name:
    < h-char-sequence >
    " q-char-sequence "

h-char-sequence:
    h-char
    h-char-sequence h-char

h-char:
    $ANYTHING BUT $\n >

q-char-sequence:
    q-char
    q-char-sequence q-char

q-char:
    $ANYTHING BUT $\n "

pp-number:
    digit
    . digit
    pp-number digit
    pp-number nondigit
    pp-number e sign
    pp-number E sign
    pp-number .

identifier:
    identifier-nondigit
    identifier identifier-nondigit
    identifier digit

identifier-nondigit:
    nondigit
    universal-character-name
    $other implementation-defined characters

nondigit:   $ONE OF
    a b c d e f g h i j k l m
    n o p q r s t u v w x y z
    A B C D E F G H I J K L M
    N O P Q R S T U V W X Y Z
    _

digit:   $ONE OF
    0 1 2 3 4 5 6 7 8 9

x-operator:
    preprocessing-op-or-punc

x-punctuator:
    preprocessing-op-or-punc

preprocessing-op-or-punc:   $ONE OF
    {       }       [       ]       #       ##      (       )
    <:      :>      <%      %>      %:      %:%:    ;       :       ...
    new     delete  ?       ::      .       .*
    +       -       *       /       %       ^       &       |       ~
    !       =       <       >       +=      -=      *=      /=      %=
    ^=      &=      |=      <<      >>      >>=     <<=     ==      !=
    <=      >=      &&      ||      ++      --      ,       ->*     ->
    and     and_eq  bitand  bitor   compl   not     not_eq
    or      or_eq   xor     xor_eq

literal:
    integer-literal
    character-literal
    floating-literal
    string-literal
    boolean-literal
    pointer-literal
    user-defined-literal

integer-literal:
    decimal-literal integer-suffix_opt
    octal-literal integer-suffix_opt
    hexadecimal-literal integer-suffix_opt

decimal-literal:
    nonzero-digit
    decimal-literal digit

octal-literal:
    0
    octal-literal octal-digit

hexadecimal-literal:
    0 x hexadecimal-digit
    0 X hexadecimal-digit
    hexadecimal-literal hexadecimal-digit

nonzero-digit:   $ONE OF
    1 2 3 4 5 6 7 8 9

octal-digit:   $ONE OF
    0 1 2 3 4 5 6 7

hexadecimal-digit:   $ONE OF
    0 1 2 3 4 5 6 7 8 9
    a b c d e f
    A B C D E F

integer-suffix:
    unsigned-suffix long-suffix_opt
    unsigned-suffix long-long-suffix_opt
    long-suffix unsigned-suffix_opt
    long-long-suffix unsigned-suffix_opt

unsigned-suffix:   $ONE OF
    u U

long-suffix:   $ONE OF
    l L

long-long-suffix:   $ONE OF
    x-ll x-LL

x-ll:
    l l

x-LL:
    L L

character-literal:
    ' c-char-sequence '
    u ' c-char-sequence '
    U ' c-char-sequence '
    L ' c-char-sequence '

c-char-sequence:
    c-char
    c-char-sequence c-char

c-char:
    $ANYTHING BUT ' \ $\n
    escape-sequence
    universal-character-name

escape-sequence:
    simple-escape-sequence
    octal-escape-sequence
    hexadecimal-escape-sequence

simple-escape-sequence:
    \ '
    \ "
    \ ?
    \ \
    \ a
    \ b
    \ f
    \ n
    \ r
    \ t
    \ v

octal-escape-sequence:
    \ octal-digit
    \ octal-digit octal-digit
    \ octal-digit octal-digit octal-digit

hexadecimal-escape-sequence:
    \ x hexadecimal-digit
    hexadecimal-escape-sequence hexadecimal-digit

floating-literal:
    fractional-constant exponent-part_opt floating-suffix_opt
    digit-sequence exponent-part floating-suffix_opt

fractional-constant:
    digit-sequence_opt . digit-sequence
    digit-sequence .

exponent-part:
    e sign_opt digit-sequence
    E sign_opt digit-sequence

sign:   $ONE OF
    + -

digit-sequence:
    digit
    digit-sequence digit

floating-suffix:   $ONE OF
    f l F L

string-literal:
    encoding-prefix_opt " s-char-sequence_opt "
    encoding-prefix_opt R raw-string

encoding-prefix:
    u 8
    u
    U
    L

s-char-sequence:
    s-char
    s-char-sequence s-char

s-char:
    $ANYTHING BUT " \ $\n
    escape-sequence
    universal-character-name

raw-string:
    " d-char-sequence_opt ( r-char-sequence_opt ) d-char-sequence_opt "

r-char-sequence:
    r-char
    r-char-sequence r-char

r-char:
    $any character except a ) followed by d-char-sequence and double quote

d-char-sequence:
    d-char
    d-char-sequence d-char

d-char:
    $ANYTHING BUT $space ( ) \ $\t $\v $\f $\n

boolean-literal:
    false
    true

pointer-literal:
    nullptr

user-defined-literal:
    user-defined-integer-literal
    user-defined-floating-literal
    user-defined-string-literal
    user-defined-character-literal

user-defined-integer-literal:
    decimal-literal ud-suffix
    octal-literal ud-suffix
    hexadecimal-literal ud-suffix

user-defined-floating-literal:
    fractional-constant exponent-part_opt ud-suffix
    digit-sequence exponent-part ud-suffix

user-defined-string-literal:
    string-literal ud-suffix

user-defined-character-literal:
    character-literal ud-suffix

ud-suffix:
    identifier
''')


parse = Grammar('cxx11', 'parse', r'''
$A.3 Basic concepts
translation--unit:
    declaration-seq_opt


$A.4 Expressions
primary-expression:
    literal
    this
    ( expression )
    id-expression
    lambda-expression

id-expression:
    unqualified-id
    qualified-id

unqualified-id:
    identifier
    operator-function-id
    conversion-function-id
    literal-operator-id
    ~ class-name
    ~ decltype-specifier
    template-id

qualified-id:
    nested-name-specifier template_opt unqualified-id
    :: identifier
    :: operator-function-id
    :: literal-operator-id
    :: template-id

nested-name-specifier:
    ::_opt type-name ::
    ::_opt namespace-name ::
    decltype-specifier ::
    nested-name-specifier identifier ::
    nested-name-specifier template_opt simple-template-id ::

lambda-expression:
    lambda-introducer lambda-declarator_opt compound-statement

lambda-introducer:
    [ lambda-capture_opt ]

lambda-capture:
    capture-default
    capture-list
    capture-default , capture-list

capture-default:
    &
    =

capture-list:
    capture ..._opt
    capture-list , capture ..._opt

capture:
    identifier
    & identifier
    this

lambda-declarator:
    ( parameter-declaration-clause ) mutable_opt exception-specification_opt attribute-specifier-seq_opt trailing-return-type_opt

postfix-expression:
    primary-expression
    postfix-expression [ expression ]
    postfix-expression [ braced-init-list ]
    postfix-expression ( expression-list_opt )
    simple-type-specifier ( expression-list_opt )
    typename-specifier ( expression-list_opt )
    simple-type-specifier { expression-list_opt }
    typename-specifier { expression-list_opt }
    postfix-expression . template_opt id-expression
    postfix-expression -> template_opt id-expression
    postfix-expression . pseudo-destructor-name
    postfix-expression -> pseudo-destructor-name
    postfix-expression ++
    postfix-expression --
    dynamic_cast < type-id > ( expression )
    static_cast < type-id > ( expression )
    reinterpret_cast < type-id > ( expression )
    const_cast < type-id > ( expression )
    typeid ( expression )
    typeid ( type-id )

expression-list:
    initializer-list

pseudo-destructor-name:
    nested-name-specifier_opt type-name :: ~ type-name
    nested-name-specifier template simple-template-id :: ~ type-name
    nested-name-specifier_opt ~ type-name
    ~ decltype-specifier

unary-expression:
    postfix-expression
    ++ cast-expression
    -- cast-expression
    unary-operator cast-expression
    sizeof unary-expression
    sizeof ( type-id )
    sizeof ... ( identifier )
    alignof ( type-id )
    noexcept-expression
    new-expression
    delete-expression

unary-operator:   $ONE OF
    * & + - ! ~

new-expression:
    ::_opt new new-placement_opt new-type-id new-initializer_opt
    ::_opt new new-placement_opt ( type-id ) new-initializer_opt

new-placement:
    ( expression-list )

new-type-id:
    type-specifier-seq new-declarator_opt

new-declarator:
    ptr-operator new-declarator_opt
    noptr-new-declarator

noptr-new-declarator:
    [ expression ] attribute-specifier-seq_opt
    noptr-new-declarator [ constant-expression ] attribute-specifier-seq_opt

new-initializer:
    ( expression-list_opt )
    braced-init-list

delete-expression:
    ::_opt delete cast-expression
    ::_opt delete [ ] cast-expression

noexcept-expression:
    noexcept ( expression )

cast-expression:
    unary-expression
    ( type-id ) cast-expression

pm-expression:
    cast-expression
    pm-expression .* cast-expression
    pm-expression ->* cast-expression

multiplicative-expression:
    pm-expression
    multiplicative-expression * pm-expression
    multiplicative-expression / pm-expression
    multiplicative-expression % pm-expression

additive-expression:
    multiplicative-expression
    additive-expression + multiplicative-expression
    additive-expression - multiplicative-expression

shift-expression:
    additive-expression
    shift-expression << additive-expression
    shift-expression >> additive-expression

relational-expression:
    shift-expression
    relational-expression < shift-expression
    relational-expression > shift-expression
    relational-expression <= shift-expression
    relational-expression >= shift-expression

equality-expression:
    relational-expression
    equality-expression == relational-expression
    equality-expression != relational-expression

and-expression:
    equality-expression
    and-expression & equality-expression

exclusive-or-expression:
    and-expression
    exclusive-or-expression ^ and-expression

inclusive-or-expression:
    exclusive-or-expression
    inclusive-or-expression | exclusive-or-expression

logical-and-expression:
    inclusive-or-expression
    logical-and-expression && inclusive-or-expression

logical-or-expression:
    logical-and-expression
    logical-or-expression || logical-and-expression

conditional-expression:
    logical-or-expression
    logical-or-expression ? expression : assignment-expression

assignment-expression:
    conditional-expression
    logical-or-expression assignment-operator initializer-clause
    throw-expression

assignment-operator:   $ONE OF
    = *= /= %= += -= >>= <<= &= ^= |=

expression:
    assignment-expression
    expression , assignment-expression

constant-expression:
    conditional-expression

$A.5 Statements
statement:
    labeled-statement
    attribute-specifier-seq_opt expression-statement
    attribute-specifier-seq_opt compound-statement
    attribute-specifier-seq_opt selection-statement
    attribute-specifier-seq_opt iteration-statement
    attribute-specifier-seq_opt jump-statement
    declaration-statement
    attribute-specifier-seq_opt try-block

labeled-statement:
    attribute-specifier-seq_opt identifier : statement
    attribute-specifier-seq_opt case constant-expression : statement
    attribute-specifier-seq_opt default : statement

expression-statement:
    expression_opt ;

compound-statement:
    { statement-seq_opt }

statement-seq:
    statement
    statement-seq statement

selection-statement:
    if ( condition ) statement
    if ( condition ) statement else statement
    switch ( condition ) statement

condition:
    expression
    attribute-specifier-seq_opt decl-specifier-seq declarator = initializer-clause
    attribute-specifier-seq_opt decl-specifier-seq declarator braced-init-list

iteration-statement:
    while ( condition ) statement
    do statement while ( expression ) ;
    for ( for-init-statement condition_opt ; expression_opt ) statement
    for ( for-range-declaration : for-range-initializer ) statement

for-init-statement:
    expression-statement
    simple-declaration

for-range-declaration:
    attribute-specifier-seq_opt decl-specifier-seq declarator

for-range-initializer:
    expression
    braced-init-list

jump-statement:
    break ;
    continue ;
    return expression_opt ;
    return braced-init-list ;
    goto identifier ;

declaration-statement:
    block-declaration


$A.6 Declarations
declaration-seq:
    declaration
    declaration-seq declaration

declaration:
    block-declaration
    function-definition
    template-declaration
    explicit-instantiation
    explicit-specialization
    linkage-specification
    namespace-definition
    empty-declaration
    attribute-declaration

block-declaration:
    simple-declaration
    asm-definition
    namespace-alias-definition
    using-declaration
    using-directive
    static_assert-declaration
    alias-declaration
    opaque-enum-declaration

alias-declaration:
    using identifier attribute-specifier-seq_opt = type-id ;

simple-declaration:
    decl-specifier-seq_opt init-declarator-list_opt ;
    attribute-specifier-seq decl-specifier-seq_opt init-declarator-list ;

static_assert-declaration:
    static_assert ( constant-expression , string-literal ) ;

empty-declaration:
    ;

attribute-declaration:
    attribute-specifier-seq ;

decl-specifier:
    storage-class-specifier
    type-specifier
    function-specifier
    friend
    typedef
    constexpr

decl-specifier-seq:
    decl-specifier attribute-specifier-seq_opt
    decl-specifier decl-specifier-seq

storage-class-specifier:
    register
    static
    thread_local
    extern
    mutable

function-specifier:
    inline
    virtual
    explicit

typedef-name:
    identifier

type-specifier:
    trailing-type-specifier
    class-specifier
    enum-specifier

trailing-type-specifier:
    simple-type-specifier
    elaborated-type-specifier
    typename-specifier
    cv-qualifier

type-specifier-seq:
    type-specifier attribute-specifier-seq_opt
    type-specifier type-specifier-seq

trailing-type-specifier-seq:
    trailing-type-specifier attribute-specifier-seq_opt
    trailing-type-specifier trailing-type-specifier-seq

simple-type-specifier:
    nested-name-specifier_opt type-name
    nested-name-specifier template simple-template-id
    char
    char16_t
    char32_t
    wchar_t
    bool
    short
    int
    long
    signed
    unsigned
    float
    double
    void
    auto
    decltype-specifier

type-name:
    class-name
    enum-name
    typedef-name
    simple-template-id

decltype-specifier:
    decltype ( expression )

elaborated-type-specifier:
    class-key attribute-specifier-seq_opt nested-name-specifier_opt identifier
    class-key nested-name-specifier_opt template_opt simple-template-id
    enum nested-name-specifier_opt identifier

enum-name:
    identifier

enum-specifier:
    enum-head { enumerator-list_opt }
    enum-head { enumerator-list , }

enum-head:
    enum-key attribute-specifier-seq_opt identifier_opt enum-base_opt
    enum-key attribute-specifier-seq_opt nested-name-specifier identifier enum-base_opt

opaque-enum-declaration:
    enum-key attribute-specifier-seq_opt identifier enum-base_opt ;

enum-key:
    enum
    enum class
    enum struct

enum-base:
    : type-specifier-seq

enumerator-list:
    enumerator-definition
    enumerator-list ,  enumerator-definition

enumerator-definition:
    enumerator
    enumerator = constant-expression

enumerator:
    identifier

namespace-name:
    original-namespace-name
    namespace-alias

original-namespace-name:
    identifier

namespace-definition:
    named-namespace-definition
    unnamed-namespace-definition

named-namespace-definition:
    original-namespace-definition
    extension-namespace-definition

original-namespace-definition:
    inline_opt namespace identifier { namespace-body }

extension-namespace-definition:
    inline_opt namespace original-namespace-name { namespace-body }

unnamed-namespace-definition:
    inline_opt namespace { namespace-body }

namespace-body:
    declaration-seq_opt

namespace-alias:
    identifier

namespace-alias-definition:
    namespace identifier = qualified-namespace-specifier ;

qualified-namespace-specifier:
    nested-name-specifier_opt namespace-name

using-declaration:
    using typename_opt nested-name-specifier unqualified-id ;
    using :: unqualified-id ;

using-directive:
    attribute-specifier-seq_opt using namespace ::_opt nested-name-specifier_opt namespace-name ;

asm-definition:
    asm ( string-literal ) ;

linkage-specification:
    extern string-literal { declaration-seq_opt }
    extern string-literal declaration

attribute-specifier-seq:
    attribute-specifier-seq_opt attribute-specifier

attribute-specifier:
    [ [ attribute-list ] ]
    alignment-specifier

alignment-specifier:
    alignas ( type-id ..._opt )
$ note: fixed from alignment-expression in the standard
    alignas ( assignment-expression ..._opt )

attribute-list:
    attribute_opt
    attribute-list , attribute_opt
    attribute ...
    attribute-list , attribute ...

attribute:
    attribute-token attribute-argument-clause_opt

attribute-token:
    identifier
    attribute-scoped-token

attribute-scoped-token:
    attribute-namespace :: identifier

attribute-namespace:
    identifier

attribute-argument-clause:
    ( balanced-token-seq )

balanced-token-seq:
    balanced-token_opt
    balanced-token-seq balanced-token

balanced-token:
    ( balanced-token-seq )
    [ balanced-token-seq ]
    { balanced-token-seq }
    $ANYTHING BUT ( ) [ ] { }


$A.7 Declarators
init-declarator-list:
    init-declarator
    init-declarator-list , init-declarator

init-declarator:
    declarator initializer_opt

declarator:
    ptr-declarator
    noptr-declarator parameters-and-qualifiers trailing-return-type

ptr-declarator:
    noptr-declarator
    ptr-operator ptr-declarator

noptr-declarator:
    declarator-id attribute-specifier-seq_opt
    noptr-declarator parameters-and-qualifiers
    noptr-declarator [ constant-expression_opt ] attribute-specifier-seq_opt
    ( ptr-declarator )

parameters-and-qualifiers:
    ( parameter-declaration-clause ) attribute-specifier-seq_opt cv-qualifier-seq_opt ref-qualifier_opt exception-specification_opt

trailing-return-type:
    -> trailing-type-specifier-seq abstract-declarator_opt

ptr-operator:
    * attribute-specifier-seq_opt cv-qualifier-seq_opt
    & attribute-specifier-seq_opt
    && attribute-specifier-seq_opt
    nested-name-specifier * attribute-specifier-seq_opt cv-qualifier-seq_opt

cv-qualifier-seq:
    cv-qualifier cv-qualifier-seq_opt

cv-qualifier:
    const
    volatile

ref-qualifier:
    &
    &&

declarator-id:
    ..._opt id-expression
    nested-name-specifier_opt class-name

type-id:
    type-specifier-seq abstract-declarator_opt

abstract-declarator:
    ptr-abstract-declarator
    noptr-abstract-declarator_opt parameters-and-qualifiers trailing-return-type
    abstract-pack-declarator

ptr-abstract-declarator:
    noptr-abstract-declarator
    ptr-operator ptr-abstract-declarator_opt

noptr-abstract-declarator:
    noptr-abstract-declarator_opt parameters-and-qualifiers
    noptr-abstract-declarator_opt [ constant-expression_opt ] attribute-specifier-seq_opt
    ( ptr-abstract-declarator )

abstract-pack-declarator:
    noptr-abstract-pack-declarator
    ptr-operator abstract-pack-declarator

noptr-abstract-pack-declarator:
    noptr-abstract-pack-declarator parameters-and-qualifiers
    noptr-abstract-pack-declarator [ constant-expression_opt ] attribute-specifier-seq_opt
    ...

parameter-declaration-clause:
    parameter-declaration-list_opt ..._opt
    parameter-declaration-list , ...

parameter-declaration-list:
    parameter-declaration
    parameter-declaration-list , parameter-declaration

parameter-declaration:
    attribute-specifier-seq_opt decl-specifier-seq declarator
    attribute-specifier-seq_opt decl-specifier-seq declarator = initializer-clause
    attribute-specifier-seq_opt decl-specifier-seq abstract-declarator_opt
    attribute-specifier-seq_opt decl-specifier-seq abstract-declarator_opt = initializer-clause

function-definition:
    attribute-specifier-seq_opt decl-specifier-seq_opt declarator virt-specifier-seq_opt function-body

function-body:
    ctor-initializer_opt compound-statement
    function-try-block
    = default ;
    = delete ;

initializer:
    brace-or-equal-initializer
    ( expression-list )

brace-or-equal-initializer:
    = initializer-clause
    braced-init-list

initializer-clause:
    assignment-expression
    braced-init-list

initializer-list:
    initializer-clause ..._opt
    initializer-list , initializer-clause ..._opt

braced-init-list:
    { initializer-list ,_opt }
    { }


$A.8 Classes
class-name:
    identifier
    simple-template-id

class-specifier:
    class-head { member-specification_opt }

class-head:
    class-key attribute-specifier-seq_opt class-head-name class-virt-specifier_opt base-clause_opt
    class-key attribute-specifier-seq_opt base-clause_opt

class-head-name:
    nested-name-specifier_opt class-name

class-virt-specifier:
    final

class-key:
    class
    struct
    union

member-specification:
    member-declaration member-specification_opt
    access-specifier : member-specification_opt

member-declaration:
    attribute-specifier-seq_opt decl-specifier-seq_opt member-declarator-list_opt ;
    function-definition ;_opt
    using-declaration
    static_assert-declaration
    template-declaration
    alias-declaration

member-declarator-list:
    member-declarator
    member-declarator-list , member-declarator

member-declarator:
    declarator virt-specifier-seq_opt pure-specifier_opt
    declarator brace-or-equal-initializer_opt
    identifier_opt attribute-specifier-seq_opt : constant-expression

virt-specifier-seq:
    virt-specifier
    virt-specifier-seq virt-specifier

virt-specifier:
    override
    final

pure-specifier:
    = 0


$A.9 Derived classes
base-clause:
    : base-specifier-list

base-specifier-list:
    base-specifier ..._opt
    base-specifier-list , base-specifier ..._opt

base-specifier:
    attribute-specifier-seq_opt base-type-specifier
    attribute-specifier-seq_opt virtual access-specifier_opt base-type-specifier
    attribute-specifier-seq_opt access-specifier virtual_opt base-type-specifier

class-or-decltype:
    nested-name-specifier_opt class-name
    decltype-specifier

base-type-specifier:
    class-or-decltype

access-specifier:
    private
    protected
    public


$A.10 Special member functions

conversion-function-id:
    operator conversion-type-id

conversion-type-id:
    type-specifier-seq conversion-declarator_opt

conversion-declarator:
    ptr-operator conversion-declarator_opt

ctor-initializer:
    : mem-initializer-list

mem-initializer-list:
    mem-initializer ..._opt
    mem-initializer , mem-initializer-list ..._opt

mem-initializer:
    mem-initializer-id ( expression-list_opt )
    mem-initializer-id braced-init-list

mem-initializer-id:
    class-or-decltype
    identifier


$A.11 Overloading
operator-function-id:
    operator x-operator

x-operator:   $ONE OF
    new delete  x-new[]     x-delete[]
    +   -   *   /   %   ^   &   |   ~
    !   =   <   >   +=  -=  *=  /=  %=
    ^=  &=  |=  <<  >>  >>= <<= ==  !=
    <=  >=  &&  ||  ++  --  ,   ->* ->
    x-()    x-[]

x-new[]:
    new [ ]

x-delete[]:
    delete [ ]

x-():
    ( )

x-[]:
    [ ]

literal-operator-id:
    operator "" identifier


$A.12 Templates
template-declaration:
    template < template-parameter-list > declaration

template-parameter-list:
    template-parameter
    template-parameter-list , template-parameter

template-parameter:
    type-parameter
    parameter-declaration

type-parameter:
    class ..._opt identifier_opt
    class identifier_opt = type-id
    typename ..._opt identifier_opt
    typename identifier_opt = type-id
    template < template-parameter-list > class identifier_opt
    template < template-parameter-list > class identifier_opt = id-expression

simple-template-id:
    template-name < template-argument-list_opt >

template-id:
    simple-template-id
    operator-function-id < template-argument-list_opt >
    literal-operator-id < template-argument-list_opt >

template-name:
    identifier

template-argument-list:
    template-argument ..._opt
    template-argument-list , template-argument ..._opt

template-argument:
    constant-expression
    type-id
    id-expression

typename-specifier:
    typename nested-name-specifier identifier
    typename nested-name-specifier template_opt simple-template-id

explicit-instantiation:
    extern_opt template declaration

explicit-specialization:
    template < > declaration


$A.13 Exception handling
try-block:
    try compound-statement handler-seq

function-try-block:
    try ctor-initializer_opt compound-statement handler-seq

handler-seq:
    handler handler-seq_opt

handler:
    catch ( exception-declaration ) compound-statement

exception-declaration:
    attribute-specifier-seq_opt type-specifier-seq declarator
    attribute-specifier-seq_opt type-specifier-seq abstract-declarator_opt
    ...

throw-expression:
    throw assignment-expression_opt

exception-specification:
    dynamic-exception-specification
    noexcept-specification

dynamic-exception-specification:
    throw ( type-id-list_opt )

type-id-list:
    type-id ..._opt
    type-id-list , type-id ..._opt

noexcept-specification:
    noexcept ( constant-expression )
    noexcept
''')


preprocessor = Grammar('cxx11', 'preprocessor', r'''
$A.14 Preprocessing directives
preprocessing-file:
    group_opt

group:
    group-part
    group group-part

group-part:
    if-section
    control-line
    text-line
    # non-directive

if-section:
    if-group elif-groups_opt else-group_opt endif-line

if-group:
    # if constant-expression new-line group_opt
    # ifdef identifier new-line group_opt
    # ifndef identifier new-line group_opt

elif-groups:
    elif-group
    elif-groups elif-group

elif-group:
    # elif constant-expression new-line group_opt

else-group:
    # else new-line group_opt

endif-line:
    # endif new-line

control-line:
    # include pp-tokens new-line
    # define identifier replacement-list new-line
    # define identifier lparen identifier-list_opt ) replacement-list new-line
    # define identifier lparen ... ) replacement-list new-line
    # define identifier lparen identifier-list , ... ) replacement-list new-line
    # undef identifier new-line
    # line pp-tokens new-line
    # error pp-tokens_opt new-line
    # pragma pp-tokens_opt new-line
    # new-line

text-line:
    pp-tokens_opt new-line

non-directive:
    pp-tokens new-line

lparen:
    $(

identifier-list:
    identifier
    identifier-list , identifier

replacement-list:
    pp-tokens_opt

pp-tokens:
    preprocessing-token
    pp-tokens preprocessing-token

new-line:
    $\n
''')
