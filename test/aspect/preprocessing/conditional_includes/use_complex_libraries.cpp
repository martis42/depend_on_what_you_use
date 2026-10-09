// Include headers from real projects which are known to be complex to preprocess
#include <gmock/gmock.h>
#include <gtest/gtest.h>

// Ensure we really did parse the googletest headers
#ifdef TEST_F
#include "preprocessing/support/lib_a.h"
#else
#include "preprocessing/support/transitive.h"
#endif

int main() {
    return 0;
}
