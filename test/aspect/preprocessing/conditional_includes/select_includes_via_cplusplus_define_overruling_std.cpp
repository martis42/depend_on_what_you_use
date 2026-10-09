#if __cplusplus == 201103
#include "preprocessing/support/lib_a.h"
#else
#include "preprocessing/support/transitive.h"
#endif

#include <iostream>

int main() {
    std::cout << __cplusplus << "\n";
    return 0;
}
