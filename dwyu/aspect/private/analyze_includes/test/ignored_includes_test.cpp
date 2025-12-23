#include "dwyu/aspect/private/analyze_includes/ignored_includes.h"

#include <boost/regex.hpp>
#include <gmock/gmock.h>
#include <gtest/gtest.h>

namespace dwyu {
namespace {

TEST(GetIgnoredIncludes, GivenNoInputReturnEmptyIgnoredIncludes) {
    const auto ignored_includes = getIgnoredIncludes("");

    EXPECT_TRUE(ignored_includes.include_paths.empty());
    EXPECT_TRUE(ignored_includes.include_patterns.empty());
}

TEST(GetIgnoredIncludes, GivenEmptyInputReturnEmptyIgnoredIncludes) {
    const auto ignored_includes =
        getIgnoredIncludes("dwyu/aspect/private/analyze_includes/test/data/cc/ignored_includes_empty.json");

    EXPECT_TRUE(ignored_includes.include_paths.empty());
    EXPECT_TRUE(ignored_includes.include_patterns.empty());
}

TEST(GetIgnoredIncludes, ReadIgnoredIncludesCorrectlyFromFile) {
    const auto ignored_includes =
        getIgnoredIncludes("dwyu/aspect/private/analyze_includes/test/data/cc/ignored_includes.json");

    // Expect we combine ignore_include_paths and extra_ignore_include_paths andremove duplicates
    EXPECT_THAT(ignored_includes.include_paths, testing::UnorderedElementsAre("foo", "bar", "foobar"));

    EXPECT_THAT(ignored_includes.include_patterns,
                testing::UnorderedElementsAre(boost::regex{"foo/.*"}, boost::regex{"bar/.*"}));
}

TEST(IsIgnoredInclude, DoNotIgnoreIncludeIfNoPatternsOrPathsGiven) {
    EXPECT_FALSE(isIgnoredInclude("some_include.h", IgnoredIncludes{}));
}

TEST(IsIgnoredInclude, IgnoreIncludeGivenPaths) {
    IgnoredIncludes ignores{};
    ignores.include_paths = {"some/include.h", "other/include.h"};

    EXPECT_TRUE(isIgnoredInclude("\"some/include.h\"", ignores));
    EXPECT_TRUE(isIgnoredInclude("<other/include.h>", ignores));

    EXPECT_FALSE(isIgnoredInclude("<not/ignored.h>", ignores));
}

TEST(IsIgnoredInclude, IgnoreIncludeGivenPatternForRootDirectory) {
    IgnoredIncludes ignores{};
    ignores.include_patterns = {boost::regex("some/.*")};

    EXPECT_TRUE(isIgnoredInclude("\"some/include.h\"", ignores));
    EXPECT_TRUE(isIgnoredInclude("<some/other/include.h>", ignores));

    EXPECT_FALSE(isIgnoredInclude("<some_include.h>", ignores));
    EXPECT_FALSE(isIgnoredInclude("<do/not/match/substring/some/include.h>", ignores));
}

TEST(IsIgnoredInclude, IgnoreIncludeGivenPatternForStartingWithAGivenString) {
    IgnoredIncludes ignores{};
    ignores.include_patterns = {boost::regex("foo/bar")};

    EXPECT_TRUE(isIgnoredInclude("\"foo/bar/include.h\"", ignores));
    EXPECT_TRUE(isIgnoredInclude("\"foo/barny/include.h\"", ignores));
    EXPECT_TRUE(isIgnoredInclude("<foo/bar_file.h>", ignores));

    EXPECT_FALSE(isIgnoredInclude("</foo/bar/include.h>", ignores));
    EXPECT_FALSE(isIgnoredInclude("<do/not/match/substring/foo/bar.h>", ignores));
    EXPECT_FALSE(isIgnoredInclude("<do/not/match/substring/foo/bar/include.h>", ignores));
}

TEST(IsIgnoredInclude, IgnoreIncludeGivenPatternForEndingWithASpecificString) {
    IgnoredIncludes ignores{};
    ignores.include_patterns = {boost::regex(".*_foo.h$")};

    EXPECT_TRUE(isIgnoredInclude("\"whatever/path/some_foo.h\"", ignores));
    EXPECT_TRUE(isIgnoredInclude("<_foo.h>", ignores));

    EXPECT_FALSE(isIgnoredInclude("<path/_some_foo.h.tpl>", ignores));
}

TEST(IsIgnoredInclude, IgnoreIncludeGivenPatternForImplicitSubstringMatch) {
    IgnoredIncludes ignores{};
    ignores.include_patterns = {boost::regex(".*_foo.h")};

    EXPECT_TRUE(isIgnoredInclude("\"whatever/path/some_foo.h\"", ignores));
    EXPECT_TRUE(isIgnoredInclude("<_foo.h>", ignores));
    EXPECT_TRUE(isIgnoredInclude("<path/_some_foo.h.tpl>", ignores));

    EXPECT_FALSE(isIgnoredInclude("\"irrelevant.h\"", ignores));
}

TEST(IsIgnoredInclude, IgnoreIncludeGivenPatternForPartialMatches) {
    IgnoredIncludes ignores{};
    ignores.include_patterns = {boost::regex(".*_foo/.*")};

    EXPECT_TRUE(isIgnoredInclude("\"whatever/path/some_foo/other/include.h\"", ignores));
    EXPECT_TRUE(isIgnoredInclude("<_foo/include.h>", ignores));

    EXPECT_FALSE(isIgnoredInclude("<path/_some_foo.h>", ignores));
    EXPECT_FALSE(isIgnoredInclude("<other_foo_bar/include.h>", ignores));
}

TEST(IsIgnoredInclude, IgnoreIncludeGivenPatternForMultiplePartialMatches) {
    IgnoredIncludes ignores{};
    ignores.include_patterns = {boost::regex(".*/foo/.*/bar/.*")};

    EXPECT_TRUE(isIgnoredInclude("\"path/foo/several/other/bar/include.h\"", ignores));
    EXPECT_TRUE(isIgnoredInclude("<path/foo/other/bar/random.txt>", ignores));
    EXPECT_TRUE(isIgnoredInclude("</foo//bar/random.txt>", ignores));

    EXPECT_FALSE(isIgnoredInclude("\"foo/bar/include.h\"", ignores));
    EXPECT_FALSE(isIgnoredInclude("<foo_bar/include.h>", ignores));
}

TEST(IsIgnoredInclude, IgnoreIncludeGivenPatternForNotMatchingASpecificRootDirectory) {
    IgnoredIncludes ignores{};
    ignores.include_patterns = {boost::regex("(?!foo).*")};

    EXPECT_TRUE(isIgnoredInclude("\"bar/include.h\"", ignores));
    EXPECT_TRUE(isIgnoredInclude("<include.h>", ignores));
    EXPECT_TRUE(isIgnoredInclude("<bar/foo/include.h>", ignores));

    EXPECT_FALSE(isIgnoredInclude("\"foo/include.h\"", ignores));
    EXPECT_FALSE(isIgnoredInclude("<foo_bar/include.h>", ignores));
    EXPECT_FALSE(isIgnoredInclude("<foo.h>", ignores));
}

TEST(IsIgnoredInclude, IgnoreIncludeGivenMultiplePatterns) {
    IgnoredIncludes ignores{};
    ignores.include_patterns = {boost::regex("some/.*"), boost::regex("other/.*")};

    EXPECT_TRUE(isIgnoredInclude("\"some/include.h\"", ignores));
    EXPECT_TRUE(isIgnoredInclude("<other/include.h>", ignores));

    EXPECT_FALSE(isIgnoredInclude("<foo/include.h>", ignores));
}

} // namespace
} // namespace dwyu
