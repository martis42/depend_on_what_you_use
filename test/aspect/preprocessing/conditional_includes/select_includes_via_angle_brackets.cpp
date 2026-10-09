// '<' and '>' are tokenized differently than raw strings of quoted include statements.
// Thus ensure we test using them explicitly.

#define TOGGLE

#define ANGLE_HEADER_B <angle_lib_b.h>
#define ANGLE_HEADER(name) <name.h>

#ifdef TOGGLE
#include <angle_lib_a.h>
#else
#include "preprocessing/support/transitive.h"
#endif

// Macro expanding to an angle bracket include path
#include ANGLE_HEADER_B

// Function like macro building an angle bracket include path
#include ANGLE_HEADER(angle_lib_c)

int main() {
    return angleLibA() + angleLibB() + angleLibC();
}
