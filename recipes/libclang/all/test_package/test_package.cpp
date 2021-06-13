#include <clang-c/Index.h>

int main(int argc, char const* argv[])
{
    const auto index = clang_createIndex(0, 0);

    if (index == nullptr)
        return 1;

    clang_disposeIndex(index);
    return 0;
}
