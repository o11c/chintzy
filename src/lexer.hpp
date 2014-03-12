#ifndef CHINTZY_LEXER_HPP
#define CHINTZY_LEXER_HPP

#include <iosfwd>
#include <string>

enum Token
{
    TOK_EOF = 0,

    TOK_PP,
    TOK_SLC,
    TOK_MLC,

    TOK_LIT,
    // All operators, parens, etc. go here
    TOK_OP,

    // All identifiers (and keywords) go under here
    TOK_TYPE,
    TOK_VALUE,
    TOK_TYXP,
    TOK_ATTR,
    TOK_IGN,
};

class Lexer
{
    std::istream& _in;
    std::ostream& _err;
    bool _macro_body;
    Token _type;
    std::string _white;
    std::string _text;

    Token flavor(std::string text);
public:
    Lexer(std::istream& in, bool mac, std::ostream& err)
    : _in(in), _err(err), _macro_body(mac), _type(TOK_EOF), _white(), _text()
    {
        pull();
    }
    Lexer(const Lexer&) = delete;
    Lexer& operator = (const Lexer&) = delete;

    Token peek(std::string& out) { out = _text; return _type; }
    void pull();

    std::string white() { return _white; }
    void die(std::string msg);
};

#endif //CHINTZY_LEXER_HPP
