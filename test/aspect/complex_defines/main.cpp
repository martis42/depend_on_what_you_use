#include <iostream>

#include "test/aspect/complex_defines/naughty.h"

#if defined(NAUGHTY_IS_ON)
#include "test/aspect/complex_defines/a.h"
#else
#include "test/aspect/complex_defines/b.h"
#endif

int main() {
#if defined(NAUGHTY_IS_ON)
    std::cout << "a: " << foo() << std::endl;
#else
    std::cout << "b: " << bar() << std::endl;
#endif
    return 0;
}
