#if __cplusplus == 201103
#include "support/lib_a.h"
#else
// If this would be included, it would fail the DWYU analysis
#include "support/transitive.h"
#endif

int main() {
    return libA();
}
