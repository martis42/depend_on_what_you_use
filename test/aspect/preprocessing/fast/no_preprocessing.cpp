#define FOO

#ifdef FOO
#include "preprocessing/support/lib_a.h"
#else
#include "preprocessing/support/lib_b.h"
#endif

int main() {
#ifdef FOO
    return libA();
#else
    return libB();
#endif
}
