#include "dwyu/aspect/private/analyze_includes/ignored_includes.h"
#include "dwyu/aspect/private/analyze_includes/include_statement.h"

#include <boost/regex.hpp>
#include <gtest/gtest.h>

#include <algorithm>

namespace dwyu {
namespace {

TEST(GetIncludeStatements, ReadingFileWithoutDataYieldsAnEmptyList) {
    const auto includes =
        getIncludeStatements({"dwyu/aspect/private/analyze_includes/test/data/cc/preprocessed_file_empty.json"}, {});

    EXPECT_TRUE(includes.empty());
}

TEST(GetIncludeStatements, ReadingFileWithoutIncludesDataYieldsAnEmptyList) {
    const auto includes = getIncludeStatements(
        {"dwyu/aspect/private/analyze_includes/test/data/cc/preprocessed_file_without_includes.json"}, {});

    EXPECT_TRUE(includes.empty());
}

TEST(GetIncludeStatements, ReadingMultipleFiles) {
    const auto includes = getIncludeStatements(
        {"dwyu/aspect/private/analyze_includes/test/data/cc/preprocessed_files_with_includes.json"}, {});

    EXPECT_EQ(includes.size(), 3);

    const auto expected_1 = std::find_if(includes.begin(), includes.end(), [](const IncludeStatement& inc) {
        return inc.file == "some/file/foo.h" && inc.include == "\"some_include.h\"" &&
               inc.resolved_include == "some/path/some_include.h";
    });
    EXPECT_TRUE(expected_1 != includes.end());

    const auto expected_2 = std::find_if(includes.begin(), includes.end(), [](const IncludeStatement& inc) {
        return inc.file == "some/file/foo.h" && inc.include == "<another/include.h>" &&
               inc.resolved_include == "some/path/another/include.h";
    });
    EXPECT_TRUE(expected_2 != includes.end());

    const auto expected_3 = std::find_if(includes.begin(), includes.end(), [](const IncludeStatement& inc) {
        return inc.file == "bar.cpp" && inc.include == "\"other_include.h\"" &&
               inc.resolved_include == "other/path/other_include.h";
    });
    EXPECT_TRUE(expected_3 != includes.end());
}

TEST(GetIncludeStatements, FilterOutIgnoredIncludes) {
    const IgnoredIncludes ignores{{"some_include.h"}, {boost::regex("another/.*")}};

    const auto includes = getIncludeStatements(
        {"dwyu/aspect/private/analyze_includes/test/data/cc/preprocessed_files_with_includes.json"}, ignores);

    ASSERT_EQ(includes.size(), 1);
    EXPECT_EQ(includes[0].file, "bar.cpp");
    EXPECT_EQ(includes[0].include, "\"other_include.h\"");
    EXPECT_EQ(includes[0].resolved_include, "other/path/other_include.h");
}

} // namespace
} // namespace dwyu
