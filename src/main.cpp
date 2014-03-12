#include <fstream>

#include "parser.hpp"

int main()
{
    // this bad interface will go away,
    // but it forces me to use the right streams
    std::ifstream in("input");
    std::ofstream out("output");
    std::ofstream err("error");
    try
    {
        parse_start(in, out, err);
    }
    catch (int x)
    {
        return x;
    }
}
