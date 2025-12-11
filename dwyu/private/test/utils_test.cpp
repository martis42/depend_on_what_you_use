#include "dwyu/private/utils.h"

#include <gtest/gtest.h>
#include <vector>

namespace dwyu {

TEST(AbortWithError, MixedTypesMessage) {
    // NOLINTNEXTLINE(cppcoreguidelines-avoid-magic-numbers)
    EXPECT_EXIT(abortWithError("Some multi ", "part message", " with mixed types: ", 42, " - ", 13.37),
                testing::ExitedWithCode(1), "Some multi part message with mixed types: 42 - 13.37");
}

TEST(ListToString, EmptyInput) {
    const auto result = listToStr({});
    EXPECT_EQ(result, "[]");
}

TEST(ListToString, OneElement) {
    const auto result = listToStr({"foo bar"});
    EXPECT_EQ(result, "[foo bar]");
}

TEST(ListToString, MultipleElements) {
    const auto result = listToStr({"foo bar", "x", "\"some text\""});
    EXPECT_EQ(result, "[foo bar, x, \"some text\"]");
}

} // namespace dwyu
