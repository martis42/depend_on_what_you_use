// This deliberately ends inside an open conditional block.
// The code processing this file is expected to not choke on this and continue working.
// We do not compile this code in the tests, thus breaking the compilation is no problem.
// Strictly speaking this violates our Assumption of use of only analyzing compiling code.
// We violate this assumption here by design to create a test case for a failing preprocessor.
#if defined(SOME_MACRO_THE_TEST_DOES_NOT_DEFINE)

// If the preprocessor breaks down this include is not parsed causing an unused dependency finding
#include "preprocessing/support/lib_a.h"

int doSomething() {
    return 42;
}
