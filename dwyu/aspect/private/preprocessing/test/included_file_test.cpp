#include "dwyu/aspect/private/preprocessing/included_file.h"

#include <boost/filesystem/path.hpp>
#include <gtest/gtest.h>

namespace bfs = boost::filesystem;

namespace dwyu {
namespace {

TEST(IsSystemInclude, VariousCases) {
    EXPECT_FALSE(isSystemInclude(""));
    EXPECT_FALSE(isSystemInclude("foo"));
    EXPECT_FALSE(isSystemInclude("\"foo\""));
    EXPECT_FALSE(isSystemInclude("<foo\""));
    EXPECT_FALSE(isSystemInclude("\"foo>"));

    EXPECT_TRUE(isSystemInclude("<foo>"));
}

TEST(IncludeWithoutQuotes, VariousCases) {
    EXPECT_EQ(includeWithoutQuotes(""), "");
    EXPECT_EQ(includeWithoutQuotes("foo"), "foo");
    EXPECT_EQ(includeWithoutQuotes("\"foo\""), "foo");
    EXPECT_EQ(includeWithoutQuotes("<foo>"), "foo");

    // For invalid cases we simply return in a "shit in shit out" fashion
    EXPECT_EQ(includeWithoutQuotes("\"foo>"), "\"foo>");
    EXPECT_EQ(includeWithoutQuotes("<foo\""), "<foo\"");
}

TEST(MakeRelativePath, VariousCases) {
    EXPECT_EQ(makeRelativePath("/foo/header.h", bfs::path{"/"}), "foo/header.h");
    EXPECT_EQ(makeRelativePath("/foo/bar/header.h", bfs::path{"/foo"}), "bar/header.h");
    EXPECT_EQ(makeRelativePath("/foo/bar/header.h", bfs::path{"/foo/bar"}), "header.h");
}

} // namespace
} // namespace dwyu
