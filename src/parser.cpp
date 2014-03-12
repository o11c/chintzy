#include "parser.hpp"

#include <map>
#include <ostream>
#include <set>

#include "lexer.hpp"

enum WhiteSpace
{
    WS_NONE,
    WS_SPACE,
    WS_NEWLINE,
    WS_UNKNOWN,
};

class Writer
{
    std::ostream& _out;
    std::ostream& _err;
    int pp_ind, ind;
public:
    Writer(std::ostream& out, std::ostream& err) : _out(out), _err(err), pp_ind(0), ind(0) {}
    Writer(const Writer&) = delete;
    Writer& operator = (const Writer&) = delete;

    void white(WhiteSpace ws)
    {
        switch (ws)
        {
        case WS_NONE:
            return;
        case WS_SPACE:
            _out << " ";
            return;
        case WS_NEWLINE:
            _out << "\n";
            return;
        case WS_UNKNOWN:
            _out << "\\ \\ ";
            return;
        }
    }

    void write(const std::string& text)
    {
        _out << text;
    }
};


void parse_start(std::istream& in_, std::ostream& out_, std::ostream& err)
{
    Lexer in(in_, false, err);
    Writer out(out_, err);
    std::string text;
    while (Token type = in.peek(text))
    {
        std::string white = in.white();
        in.pull();
        out.write(white);
        out.write(text);
    }
    out.white(WS_NEWLINE);
}
