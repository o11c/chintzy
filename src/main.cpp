#include <fstream>

#include "parser.hpp"

int main(int argc, char **argv)
{
    if (argc != 4)
    {
        return 1;
    }
    std::ifstream in(argv[1]);
    std::ofstream out(argv[2]);
    std::ofstream err(argv[3]);
    try
    {
        parse_start(in, out, err);
    }
    catch (int x)
    {
        return x;
    }
}
