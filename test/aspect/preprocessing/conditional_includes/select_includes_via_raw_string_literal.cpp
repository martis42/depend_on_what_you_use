// Includes in a raw string literal should be ignored
const char* const text = R"(
#include "preprocessing/support/transitive.h"
)";

// If the raw string literal is not processed correctly, this include is not reached
#include "preprocessing/support/lib_a.h"

int main() {
    static_cast<void>(text);
    return libA();
}
