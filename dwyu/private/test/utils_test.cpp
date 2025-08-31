#include "dwyu/private/utils.h"

#include <gtest/gtest.h>
#include <string>
#include <vector>

namespace dwyu {

TEST(AbortWithError, MixedTypesMessage) {
    EXPECT_EXIT(abortWithError("Some multi ", "part message", " with mixed types: ", 42, " - ", 13.37),
                testing::ExitedWithCode(1), "Some multi part message with mixed types: 42 - 13.37");
}

} // namespace dwyu
