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
# lex 0 as its own token, add a -> integer-literal case in the parser
#
# since $ is invalid, use it as an escape of sorts (also section markers)

from ..rules import Grammar

# Annex A: Grammar summary

lex = Grammar('cxx98', 'lex', r'''
$2.11 Keywords, Table 3 & 4
x-keyword:   $ONE OF
    asm         do              if                  return      typedef
    auto        double          inline              short       typeid
    bool        dynamic_cast    int                 signed      typename
    break       else            long                sizeof      union
    case        enum            mutable             static      unsigned
    catch       explicit        namespace           static_cast using
    char        export          new                 struct      virtual
    class       extern          operator            switch      void
    const       false           private             template    volatile
    const_cast  float           protected           this        wchar_t
    continue    for             public              throw       while
    default     friend          register            true
    delete      goto            reinterpret_cast    try

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
    string-literal
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
    nondigit
    identifier nondigit
    identifier digit

nondigit:   $ONE OF
    universal-character-name
    _
    a b c d e f g h i j k l m
    n o p q r s t u v w x y z
    A B C D E F G H I J K L M
    N O P Q R S T U V W X Y Z

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
    long-suffix unsigned-suffix_opt

unsigned-suffix:   $ONE OF
    u U

long-suffix:   $ONE OF
    l L

character-literal:
    ' c-char-sequence '
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

simple-escape-sequence:   $ONE OF
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
    " s-char-sequence_opt "
    L " s-char-sequence_opt "

s-char-sequence:
    s-char
    s-char-sequence s-char

s-char:
    $ANYTHING BUT " \ $\n
    escape-sequence
    universal-character-name

boolean-literal:
    false
    true
''')


parse = Grammar('cxx98', 'parse', r'''
$A.3 Basic concepts
translation--unit:
    declaration-seq_opt


$A.4 Expressions
primary-expression:
    literal
    this
    ( expression )
    id-expression

id-expression:
    unqualified-id
    qualified-id

unqualified-id:
    identifier
    operator-function-id
    conversion-function-id
    ~ class-name
    template-id

qualified-id:
    ::_opt nested-name-specifier template_opt unqualified-id
    :: identifier
    :: operator-function-id
    :: template-id

nested-name-specifier:
    class-or-namespace-name :: nested-name-specifier_opt
    class-or-namespace-name :: template nested-name-specifier

class-or-namespace-name:
    class-name
    namespace-name

postfix-expression:
    primary-expression
    postfix-expression [ expression ]
    postfix-expression ( expression-list_opt )
    simple-type-specifier ( expression-list_opt )
    typename ::_opt nested-name-specifier identifier ( expression-list_opt )
    typename ::_opt nested-name-specifier template_opt template-id ( expression-list_opt )
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
    assignment-expression
    expression-list , assignment-expression

pseudo-destructor-name:
    ::_opt nested-name-specifier_opt type-name :: ~ type-name
    ::_opt nested-name-specifier template template-id :: ~ type-name
    ::_opt nested-name-specifier_opt ~ type-name

unary-expression:
    postfix-expression
    ++ cast-expression
    -- cast-expression
    unary-operator cast-expression
    sizeof unary-expression
    sizeof ( type-id )
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
    direct-new-declarator

direct-new-declarator:
    [ expression ]
    direct-new-declarator [ constant-expression ]

new-initializer:
    ( expression-list_opt )

delete-expression:
    ::_opt delete cast-expression
    ::_opt delete [ ] cast-expression

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
    logical-or-expression assignment-operator assignment-expression
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
    expression-statement
    compound-statement
    selection-statement
    iteration-statement
    jump-statement
    declaration-statement
    try-block

labeled-statement:
    identifier : statement
    case constant-expression : statement
    default : statement

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
    type-specifier-seq declarator = assignment-expression

iteration-statement:
    while ( condition ) statement
    do statement while ( expression ) ;
    for ( for-init-statement condition_opt ; expression_opt ) statement

for-init-statement:
    expression-statement
    simple-declaration

jump-statement:
    break ;
    continue ;
    return expression_opt ;
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

block-declaration:
    simple-declaration
    asm-definition
    namespace-alias-definition
    using-declaration
    using-directive

simple-declaration:
    decl-specifier-seq_opt init-declarator-list_opt ;

decl-specifier:
    storage-class-specifier
    type-specifier
    function-specifier
    friend
    typedef

decl-specifier-seq:
    decl-specifier-seq_opt decl-specifier

storage-class-specifier:
    auto
    register
    static
    extern
    mutable

function-specifier:
    inline
    virtual
    explicit

typedef-name:
    identifier

type-specifier:
    simple-type-specifier
    class-specifier
    enum-specifier
    elaborated-type-specifier
    cv-qualifier

simple-type-specifier:
    ::_opt nested-name-specifier_opt type-name
    ::_opt nested-name-specifier template template-id
    char
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

type-name:
    class-name
    enum-name
    typedef-name

elaborated-type-specifier:
    class-key ::_opt nested-name-specifier_opt identifier
    enum ::_opt nested-name-specifier_opt identifier
    typename ::_opt nested-name-specifier identifier
    typename ::_opt nested-name-specifier template_opt template-id

enum-name:
    identifier

enum-specifier:
    enum identifier_opt { enumerator-list_opt }

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
    namespace identifier { namespace-body }

extension-namespace-definition:
    namespace original-namespace-name { namespace-body }

unnamed-namespace-definition:
    namespace { namespace-body }

namespace-body:
    declaration-seq_opt

namespace-alias:
    identifier

namespace-alias-definition:
    namespace identifier = qualified-namespace-specifier ;

qualified-namespace-specifier:
    ::_opt nested-name-specifier_opt namespace-name

using-declaration:
    using typename_opt ::_opt nested-name-specifier unqualified-id ;
    using :: unqualified-id ;

using-directive:
    using namespace ::_opt nested-name-specifier_opt namespace-name ;

asm-definition:
    asm ( string-literal ) ;

linkage-specification:
    extern string-literal { declaration-seq_opt }
    extern string-literal declaration


$A.7 Declarators
init-declarator-list:
    init-declarator
    init-declarator-list , init-declarator

init-declarator:
    declarator initializer_opt

declarator:
    direct-declarator
    ptr-operator declarator

direct-declarator:
    declarator-id
    direct-declarator ( parameter-declaration-clause ) cv-qualifier-seq_opt exception-specification_opt
    direct-declarator [ constant-expression_opt ]
    ( declarator )

ptr-operator:
    * cv-qualifier-seq_opt
    &
    ::_opt nested-name-specifier * cv-qualifier-seq_opt

cv-qualifier-seq:
    cv-qualifier cv-qualifier-seq_opt

cv-qualifier:
    const
    volatile

declarator-id:
    id-expression
    ::_opt nested-name-specifier_opt type-name

type-id:
    type-specifier-seq abstract-declarator_opt

type-specifier-seq:
    type-specifier type-specifier-seq_opt

abstract-declarator:
    ptr-operator abstract-declarator_opt
    direct-abstract-declarator

direct-abstract-declarator:
    direct-abstract-declarator_opt ( parameter-declaration-clause ) cv-qualifier-seq_opt exception-specification_opt
    direct-abstract-declarator_opt [ constant-expression_opt ]
    ( abstract-declarator )

parameter-declaration-clause:
    parameter-declaration-list_opt ..._opt
    parameter-declaration-list , ...

parameter-declaration-list:
    parameter-declaration
    parameter-declaration-list , parameter-declaration

parameter-declaration:
    decl-specifier-seq declarator
    decl-specifier-seq declarator = assignment-expression
    decl-specifier-seq abstract-declarator_opt
    decl-specifier-seq abstract-declarator_opt = assignment-expression

function-definition:
    decl-specifier-seq_opt declarator ctor-initializer_opt function-body
    decl-specifier-seq_opt declarator function-try-block

function-body:
    compound-statement

initializer:
    = initializer-clause
    ( expression-list )

initializer-clause:
    assignment-expression
    { initializer-list ,_opt }
    { }

initializer-list:
    initializer-clause
    initializer-list , initializer-clause


$A.8 Classes
class-name:
    identifier
    template-id

class-specifier:
    class-head { member-specification_opt }

class-head:
    class-key identifier_opt base-clause_opt
    class-key nested-name-specifier identifier base-clause_opt
    class-key nested-name-specifier_opt template-id base-clause_opt

class-key:
    class
    struct
    union

member-specification:
    member-declaration member-specification_opt
    access-specifier : member-specification_opt

member-declaration:
    decl-specifier-seq_opt member-declarator-list_opt ;
    function-definition ;_opt
    ::_opt nested-name-specifier template_opt unqualified-id ;
    using-declaration
    template-declaration

member-declarator-list:
    member-declarator
    member-declarator-list , member-declarator

member-declarator:
    declarator pure-specifier_opt
    declarator constant-initializer_opt
    identifier_opt : constant-expression

pure-specifier:
    = 0

constant-initializer:
    = constant-expression


$A.9 Derived classes
base-clause:
    : base-specifier-list

base-specifier-list:
    base-specifier
    base-specifier-list , base-specifier

base-specifier:
    ::_opt nested-name-specifier_opt class-name
    virtual access-specifier_opt :: nested-name-specifier_opt class-name
    access-specifier virtual_opt :: nested-name-specifier_opt class-name

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
    mem-initializer
    mem-initializer , mem-initializer-list

mem-initializer:
    mem-initializer-id ( expression-list_opt )

mem-initializer-id:
    ::_opt nested-name-specifier_opt class-name
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


$A.12 Templates
template-declaration:
    export_opt template < template-parameter-list > declaration

template-parameter-list:
    template-parameter
    template-parameter-list , template-parameter

template-parameter:
    type-parameter
    parameter-declaration

type-parameter:
    class identifier_opt
    class identifier_opt = type-id
    typename identifier_opt
    typename identifier_opt = type-id
    template < template-parameter-list > class identifier_opt
    template < template-parameter-list > class identifier_opt = id-expression

template-id:
    template-name < template-argument-list_opt >

template-name:
    identifier

template-argument-list:
    template-argument
    template-argument-list , template-argument

template-argument:
    assignment-expression
    type-id
    id-expression

explicit-instantiation:
    template declaration

explicit-specialization:
    template < > declaration


$A.13 Exception handling
try-block:
    try compound-statement handler-seq

function-try-block:
    try ctor-initializer_opt function-body handler-seq

handler-seq:
    handler handler-seq_opt

handler:
    catch ( exception-declaration ) compound-statement

exception-declaration:
    type-specifier-seq declarator
    type-specifier-seq abstract-declarator
    type-specifier-seq
    ...

throw-expression:
    throw assignment-expression_opt

exception-specification:
    throw ( type-id-list_opt )

type-id-list:
    type-id
    type-id-list , type-id
''')


preprocessor = Grammar('cxx98', 'preprocessor', r'''
$A.14 Preprocessing directives
preprocessing-file:
    group_opt

group:
    group-part
    group group-part

group-part:
    pp-tokens_opt new-line
    if-section
    control-line

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
    # undef identifier new-line
    # line pp-tokens new-line
    # error pp-tokens_opt new-line
    # pragma pp-tokens_opt new-line
    # new-line

lparen:
    $(

$ missing from std
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
