#include "lexer.hpp"

#include <cassert>

#include <istream>
#include <map>
#include <set>

// keys are operators
// values are the characters that can make a longer operator
std::map<std::string, std::set<char>> operators =
{
    // Only inside a macro definition
    {"#", {'#'}},
    {"##", {}},

    {"+", {'+', '='}},
    {"++", {}},
    {"+=", {}},

    {"-", {'-', '=', '>'}},
    {"--", {}},
    {"-=", {}},
    {"->", {'*'}},
    {"->*", {}},

    {"*", {'='}},
    {"*=", {}},

    {"/", {'=', '/', '*'}},
    {"/=", {}},
    // Comments are handled in post step
    {"//", {}},
    {"/*", {}},

    {"%", {'='}},
    {"%=", {}},

    {"=", {'='}},
    {"==", {}},

    {"!", {'='}},
    {"!=", {}},

    {"~", {}},

    {"|", {'|', '='}},
    {"||", {}},
    {"|=", {}},

    {"&", {'&', '='}},
    {"&&", {}},
    {"&=", {}},

    {"^", {'='}},
    {"^=", {}},

    {"<", {'<', '='}},
    {"<=", {}},
    {"<<", {'='}},
    {"<<=", {}},

    {">", {'>', '='}},
    {">=", {}},
    {">>", {'='}},
    {">>=", {}},

    {".", {'.', '*'}},
    {"..", {'.'}},
    {".*", {}},
    {"...", {}},

    {":", {':'}},
    {"::", {}},

    {"(", {}},
    {")", {}},

    {"[", {}},
    {"]", {}},

    {"{", {}},
    {"}", {}},

    {"?", {}},

    {",", {}},
    {";", {}},
};

std::map<std::string, std::string> operator_map =
{
    {"and",     "&&"},
    {"and_eq",  "&="},
    {"bitand",  "&"},
    {"bitor",   "|"},
    {"compl",   "~"},
    {"not",     "!"},
    {"not_eq",  "!="},
    {"or",      "||"},
    {"or_eq",   "|="},
    {"xor",     "^"},
    {"xor_eq",  "^="},
};

std::set<char> str_to_set(std::string s)
{
    return std::set<char>(s.begin(), s.end());
}

#define UPPER "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
#define LOWER "abcdefghijklmnopqrstuvwxyz"
#define DIGITS "0123456789"
std::set<char> word_first = str_to_set(UPPER LOWER "_$@");
std::set<char> word_rest = str_to_set(UPPER LOWER "_$@" DIGITS);
std::set<char> whitespace = str_to_set(" \t\n\r\v\f");
std::set<char> digits = str_to_set(DIGITS);
std::set<char> higits = str_to_set(DIGITS "ABCDEF" "abcdef");

void Lexer::die(std::string msg)
{
    _err << msg << std::endl;
    _err << "This error is fatal. Dumping rest of istream ..." << std::endl;
    _err << _in.rdbuf();
    throw 1;
}

void Lexer::pull()
{
    _white = "";
    _text = "";

    char c;

    // skipping whitespace
    while (true)
    {
        _in.get(c);

        if (!_in)
        {
            _type = TOK_EOF;
            return;
        }
        if (whitespace.count(c))
        {
            _white += c;
            continue;
        }

        if (c != '\\')
            break;

        _white += c;
        _in.get(c);
        if (!_in || !whitespace.count(c))
            die("toplevel backslash not followed by whitespace");
        _white += c;
    }

    _text += c;
    auto it = operators.find(_text);
    if (it != operators.end())
    {
        while (true)
        {
            if (_in.get(c) && it->second.count(c))
            {
                _text += c;
                it = operators.find(_text);
                assert (it != operators.end());
                continue;
            }
            else
            {
                _in.unget();
                break;
            }
        }
        if (_text == "##" && !_macro_body)
        {
            die("'##' is only valid in a macro body");
        }
        if (_text == "#" && !_macro_body)
        {
            while ((_in.get(c)) && (c != '\n'))
            {
                if (c == '\\')
                {
                    _in.get(c);
                    if (!_in || !whitespace.count(c))
                        die("macro-level backslash not followed by whitespace");
                }
                _text += c;
            }
            // whatever?
            _in.unget();
            _type = TOK_PP;
            return;
        }
        if (_text == "//")
        {
            while ((_in.get(c)) && (c != '\n'))
            {
                if (c == '\\')
                {
                    _in.get(c);
                    if (!_in || !whitespace.count(c))
                        die("comment-level backslash not followed by whitespace");
                }
                _text += c;
            }
            // whatever!
            _in.unget();
            _type = TOK_SLC;
            return;
        }
        if (_text == "/*")
        {
            bool prev_star = false;
            while (true)
            {
                _in.get(c);
                if (!_in)
                    die("unclosed block comment");
                _text += c;
                prev_star = c == '*';
                if (prev_star && c == '/')
                    break;
            }
            _type = TOK_MLC;
            return;
        }
        _type = TOK_OP;
        return;
    }
    // not an operator or comment
    if (c == '"' || c == '\'')
    {
        char match = c;
        while (true)
        {
            _in.get(c);
            if (!_in)
                die("unclosed string/char literal");
            _text += c;
            if (c == match)
                break;
            if (c == '\\')
            {
                _in.get(c);
                if (!_in)
                    die("EOF after backslash in string/char literal");
                // we don't care if it's valid or not, just add it
                _text += c;
            }
        }
        _type = TOK_LIT;
        return;
    }
    if (digits.count(c))
    {
        std::set<char> *digs = &digits;
        if (c == '0')
        {
            if ((_in.get(c)) && (c == 'x' || c == 'X'))
            {
                digs = &higits;
                _text += c;
            }
            else
                _in.unget();
        }
        while ((_in.get(c)) && digs->count(c))
        {
            _text += c;
        }
        _in.unget();
        _type = TOK_LIT;
        return;
    }
    if (word_first.count(c))
    {
        while ((_in.get(c)) && word_rest.count(c))
            _text += c;
        _in.unget();
        _type = flavor(_text);
        return;
    }
    die("Unknown character");
}

std::map<std::string, Token> _flavors =
{
    {"_", TOK_VALUE},
    {"char", TOK_TYPE},
    {"int", TOK_TYPE},
};

Token Lexer::flavor(std::string text)
{
    auto it = _flavors.find(text);
    if (it != _flavors.end())
        return it->second;
    bool has_caps = false;
    bool all_caps = true;
    for (char c : text)
    {
        if ('A' <= c && c <= 'Z')
            has_caps = true;
        else
            all_caps = false;
    }

    if (all_caps)
    {
        // LIKE_THIS
        return TOK_VALUE;
    }
    if ('A' <= text[0] && text[0] <= 'Z')
    {
        // LikeThis
        return TOK_TYPE;
    }
    if (has_caps)
    {
        // likeThis
        return TOK_VALUE;
    }
    // like_this
    return TOK_VALUE;
}
