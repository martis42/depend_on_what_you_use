// This code only passes the DWYU analysis if the first branch is taken.
#if __has_include("has_include/lib_a.h")
// If this is not being processed, we see a unused dependency error
#include "has_include/lib_a.h"
#else
// If the preprocessor takes this branch, we fail the test due to using a header from a transitive dependency
#include "has_include/transitive_dep.h"
#endif

// Ensure the preprocessing does not always take the same branch by testing the inverse logic compared to the first test
// setup. The code below only passes the DWYU analysis if the else branch is taken.
#if __has_include("not/existing.h")
#include "has_include/transitive_dep.h"
#else
#include "has_include/lib_b.h"
#endif
