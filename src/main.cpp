#include <fstream>

#include "parse.hpp"

int main()
{
    // this bad interface will go away,
    // but it forces me to use the right streams
    std::ifstream in("input");
    std::ofstream out("output");
    parse_root(in, out);
}
