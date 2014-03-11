#include "parse.hpp"


void parse_root(std::istream& in, std::ostream& out)
{
    out << in.rdbuf();
}
