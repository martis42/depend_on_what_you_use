#include "dwyu/aspect/private/preprocessing/preprocessing_hooks.h"

#include <gtest/gtest.h>
#include <string>
#include <vector>

namespace dwyu {

TEST(IsSystemInclude, EmptyInput) {
    EXPECT_EQ(isSystemInclude(""), false);
}

TEST(IsSystemInclude, NoQuoting) {
    EXPECT_EQ(isSystemInclude("foo"), false);
}

TEST(IsSystemInclude, QuoteInclude) {
    EXPECT_EQ(isSystemInclude("\"foo\""), false);
}

TEST(IsSystemInclude, AngleBracketInclude) {
    EXPECT_EQ(isSystemInclude("<foo>"), true);
}

TEST(IncludeWithoutQuotes, EmptyInput) {
    EXPECT_EQ(includeWithoutQuotes(""), "");
}

TEST(IncludeWithoutQuotes, NoQuoting) {
    EXPECT_EQ(includeWithoutQuotes("foo"), "foo");
}

TEST(IncludeWithoutQuotes, QuoteInclude) {
    EXPECT_EQ(includeWithoutQuotes("\"foo\""), "foo");
}

TEST(IncludeWithoutQuotes, AngleBracketInclude) {
    EXPECT_EQ(includeWithoutQuotes("<foo>"), "foo");
}

} // namespace dwyu
