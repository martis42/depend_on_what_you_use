#if __cplusplus == 201103
#include "preprocessing/support/lib_a.h"
#else
// If this would be included, it would fail the DWYU analysis
#include "preprocessing/support/transitive.h"
#endif

#include <iostream>

int main() {
    std::cout << __cplusplus << "\n";
    return 0;
}
