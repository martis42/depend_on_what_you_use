#include <iostream>
#include <string>

#define SOME_VARIADIC_MACRO(fmt, ...) fmt

std::string someFunction() {
    return SOME_VARIADIC_MACRO("some message");
}

// If the preprocessor dies due to the variadic macro, this include will not be found causing an unused dependency finding
#include "preprocessing/support/lib_a.h"

int main() {
    std::cout << someFunction() << "\n";
    return 0;
}
