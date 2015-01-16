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
# since $ is invalid, use it as an escape of sorts (also section markers)

from ..rules import Grammar

# Annex B: Language syntax summary

lex = Grammar('c89', 'lex', r'''
$B.1 Lexical grammar

$B.1.1 Tokens
token:
    keyword
    identifier
    constant
    string-literal
    operator
    punctuator

preprocessing-token:
    header-name
    identifier
    pp-number
    character-constant
    string-literal
    operator
    punctuator
    $each non-white-space character that cannot be one of the above


$B.1.2 Keywords
keyword:   $ONE OF
    auto        double      int         struct
    break       else        long        switch
    case        enum        register    typedef
    char        extern      return      union
    const       float       short       unsigned
    continue    for         signed      void
    default     goto        sizeof      volatile
    do          if          static      while


$B.1.3 Identifiers
identifier:
    nondigit
    identifier nondigit
    identifier digit

nondigit:   $ONE OF
    _
    a b c d e f g h i j k l m
    n o p q r s t u v w x y z
    A B C D E F G H I J K L M
    N O P Q R S T U V W X Y Z

digit:   $ONE OF
    0 1 2 3 4 5 6 7 8 9


$B.1.4 Constants
constant:
    floating-constant
    integer-constant
    enumeration-constant
    character-constant

floating-constant:
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

integer-constant:
    decimal-constant integer-suffix_opt
    octal-constant integer-suffix_opt
    hexadecimal-constant integer-suffix_opt

octal-constant:
    0
    octal-constant octal-digit

decimal-constant:
    nonzero-digit
    decimal-constant digit

hexadecimal-constant:
    0 x hexadecimal-digit
    0 X hexadecimal-digit
    hexadecimal-constant hexadecimal-digit

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

enumeration-constant:
    identifier

character-constant:
    ' c-char-sequence '
    L ' c-char-sequence '

c-char-sequence:
    c-char
    c-char-sequence c-char

c-char:
    $ANYTHING BUT ' \ $\n
    escape-sequence

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


$B.1.5 String literals
string-literal:
    " s-char-sequence_opt "
    L " s-char-sequence_opt "

s-char-sequence:
    s-char
    s-char-sequence s-char

s-char:
    $ANYTHING BUT " \ $\n
    escape-sequence


$B.1.6 Operators
operator:   $ONE OF
    [ ] ( ) .  ->
    ++ -- & * + - ~ !  sizeof
    / % << >> < > <= >= == != ^ | && ||
    ? :
    = *= /= %= += -= <<= >>= &= ^= |=
    , # ##


$B.1.7 Punctuator
punctuator:   $ONE OF
    [ ] ( ) { } * , : = ; ... #


$B.1.8 Header names
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


$B.1.9 Preprocessing numbers
pp-number:
    digit
    . digit
    pp-number digit
    pp-number nondigit
    pp-number e sign
    pp-number E sign
    pp-number .
''')


parse = Grammar('c89', 'parse', r'''
$B.2 Phrase structure grammar

$B.2.1 Expressions
primary-expression:
    identifier
    constant
    string-literal
    ( expression )

postfix-expression:
    primary-expression
    postfix-expression [ expression ]
    postfix-expression ( argument-expression-list_opt )
    postfix-expression . identifier
    postfix-expression -> identifier
    postfix-expression ++
    postfix-expression --

argument-expression-list:
    assignment-expression
    argument-expression-list , assignment-expression

unary-expression:
    postfix-expression
    ++ unary-expression
    -- unary-expression
    unary-operator cast-expression
    sizeof unary-expression
    sizeof ( type-name )

unary-operator:   $ONE OF
    & * + - ~ !

cast-expression:
    unary-expression
    ( type-name ) cast-expression

multiplicative-expression:
    cast-expression
    multiplicative-expression * cast-expression
    multiplicative-expression / cast-expression
    multiplicative-expression % cast-expression

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

AND-expression:
    equality-expression
    AND-expression & equality-expression

exclusive-OR-expression:
    AND-expression
    exclusive-OR-expression ^ AND-expression

inclusive-OR-expression:
    exclusive-OR-expression
    inclusive-OR-expression | exclusive-OR-expression

logical-AND-expression:
    inclusive-OR-expression
    logical-AND-expression && inclusive-OR-expression

logical-OR-expression:
    logical-AND-expression
    logical-OR-expression || logical-AND-expression

conditional-expression:
    logical-OR-expression
    logical-OR-expression ? expression : conditional-expression

assignment-expression:
    conditional-expression
    unary-expression assignment-operator assignment-expression

assignment-operator:   $ONE OF
    = *= /= %= += -= <<= >>= &= ^= |=

expression:
    assignment-expression
    expression , assignment-expression

constant-expression:
    conditional-expression


$B.2.2 Declarations
declaration:
    declaration-specifiers init-declarator-list_opt ;

declaration-specifiers:
    storage-class-specifier declaration-specifiers_opt
    type-specifier declaration-specifiers_opt
    type-qualifier declaration-specifiers_opt

init-declarator-list:
    init-declarator
    init-declarator-list , init-declarator

init-declarator:
    declarator
    declarator = initializer

storage-class-specifier:
    typedef
    extern
    static
    auto
    register

type-specifier:
    void
    char
    short
    int
    long
    float
    double
    signed
    unsigned
    struct-or-union-specifier
    enum-specifier
    typedef-name

struct-or-union-specifier:
    struct-or-union identifier_opt { struct-declaration-list }
    struct-or-union identifier

struct-or-union:
    struct
    union

struct-declaration-list:
    struct-declaration
    struct-declaration-list struct-declaration

struct-declaration:
    specifier-qualifier-list struct-declarator-list ;

specifier-qualifier-list:
    type-specifier specifier-qualifier-list_opt
    type-qualifier specifier-qualifier-list_opt

struct-declarator-list:
    struct-declarator
    struct-declarator-list , struct-declarator

struct-declarator:
    declarator
    declarator_opt : constant-expression

enum-specifier:
    enum identifier_opt { enumerator-list }
    enum identifier

enumerator-list:
    enumerator
    enumerator-list , enumerator

enumerator:
    enumeration-constant
    enumeration-constant = constant-expression

type-qualifier:
    const
    volatile

declarator:
    pointer_opt direct-declarator

direct-declarator:
    identifier
    ( declarator )
    direct-declarator [ constant-expression_opt ]
    direct-declarator ( parameter-type-list )
    direct-declarator ( identifier-list_opt )

pointer:
    * type-qualifier-list_opt
    * type-qualifier-list_opt pointer

type-qualifier-list:
    type-qualifier
    type-qualifier-list type-qualifier

parameter-type-list:
    parameter-list
    parameter-list , ...

parameter-list:
    parameter-declaration
    parameter-list , parameter-declaration

parameter-declaration:
    declaration-specifiers declarator
    declaration-specifiers abstract-declarator_opt

identifier-list:
    identifier
    identifier-list , identifier

type-name:
    specifier-qualifier-list abstract-declarator_opt

abstract-declarator:
    pointer
    pointer_opt direct-abstract-declarator

direct-abstract-declarator:
    ( abstract-declarator )
    direct-abstract-declarator_opt [ constant-expression_opt ]
    direct-abstract-declarator_opt ( parameter-type-list_opt )

typedef-name:
    identifier

initializer:
    assignment-expression
    { initializer-list }
    { initializer-list , }

initializer-list:
    initializer
    initializer-list , initializer


$B.2.3 Statements
statement:
    labeled-statement
    compound-statement
    expression-statement
    selection-statement
    iteration-statement
    jump-statement

labeled-statement:
    identifier : statement
    case constant-expression : statement
    default : statement

compound-statement:
    { declaration-list_opt statement-list_opt }

declaration-list:
    declaration
    declaration-list declaration

statement-list:
    statement
    statement-list statement

expression-statement:
    expression_opt ;

selection-statement:
    if ( expression ) statement
    if ( expression ) statement else statement
    switch ( expression ) statement

iteration-statement:
    while ( expression ) statement
    do statement while ( expression ) ;
    for ( expression_opt ; expression_opt ; expression_opt ) statement

jump-statement:
    goto identifier ;
    continue ;
    break ;
    return expression_opt ;


$B.2.4 External definitions
translation-unit:
    external-declaration
    translation-unit external-declaration

external-declaration:
    function-definition
    declaration

function-definition:
    declaration-specifiers_opt declarator declaration-list_opt compound-statement
''')


preprocessor = Grammar('c89', 'preprocessor', r'''
$B.3 Preprocessing directives
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

replacement-list:
    pp-tokens_opt

pp-tokens:
    preprocessing-token
    pp-tokens preprocessing-token

new-line:
    $\n
''')
