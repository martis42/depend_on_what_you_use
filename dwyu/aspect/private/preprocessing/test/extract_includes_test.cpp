#include "dwyu/aspect/private/preprocessing/extract_includes.h"

#include <fstream>
#include <gtest/gtest.h>
#include <set>
#include <sstream>
#include <string>

namespace dwyu {

TEST(extractIncludes, EmptyResultForEmptyInput) {
    std::istringstream test_input{std::string{""}};

    const auto result = extractIncludes(test_input);

    EXPECT_TRUE(result.empty());
}

TEST(extractIncludes, EmptyResultForNoIncludes) {
    std::stringstream text{};
    text << "Some unrelated" << "\n";
    text << "stuff here" << "\n";

    const auto result = extractIncludes(text);

    EXPECT_TRUE(result.empty());
}

TEST(extractIncludes, ExtractIncludes) {
    std::stringstream text{};
    text << "#include \"foo.h\"" << "\n";
    text << "  #include<some/path.h>" << "\n";
    text << "#include     <no_extension>" << "\n";

    const auto result = extractIncludes(text);

    const std::set<std::string> expected = {"foo.h", "some/path.h", "no_extension"};
    EXPECT_EQ(result, expected);
}

TEST(extractIncludes, IgnoreUnrelatedPreprocessorStatements) {
    std::stringstream text{};
    text << "#ifdef \"foo.h\"" << "\n";
    text << "#incclude \"bar.h\"" << "\n";

    const auto result = extractIncludes(text);

    EXPECT_TRUE(result.empty());
}

TEST(extractIncludes, IgnoreCommentedLines) {
    std::stringstream text{};
    text << "// #include <foo.h>" << "\n";
    text << "//#include \"bar.h\"" << "\n";

    const auto result = extractIncludes(text);

    EXPECT_TRUE(result.empty());
}

TEST(extractIncludes, IgnoreCStyleComments) {
    std::stringstream text{};
    text << "/*\n";
    text << "#include <foo.h>" << "\n";
    text << "#include \"bar.h\"" << "\n";
    text << "*\\\n";

    const auto result = extractIncludes(text);

    EXPECT_TRUE(result.empty());
}

TEST(extractIncludes, IgnoreCommentAfterRealInclude) {
    std::stringstream text{};
    text << "#include <foo.h> // #include <bar.h>" << "\n";

    const auto result = extractIncludes(text);

    const std::set<std::string> expected = {"foo.h"};
    EXPECT_EQ(result, expected);
}

TEST(extractIncludes, IgnoreCStyleCommentsInLineWithRealInclude) {
    std::stringstream text{};
    text << "/*#include <foo.h>*/ #include <bar.h> /*#include <foobar.h>*/" << "\n";

    const auto result = extractIncludes(text);

    const std::set<std::string> expected = {"bar.h"};
    EXPECT_EQ(result, expected);
}

TEST(extractIncludes, CloseCStyleCommentNoMatterHowOftenOpened) {
    std::stringstream text{};
    text << "/* /* /* #include <foo.h>*/ #include <bar.h>" << "\n";

    const auto result = extractIncludes(text);

    const std::set<std::string> expected = {"bar.h"};
    EXPECT_EQ(result, expected);
}

TEST(extractIncludes, IgnoreCStyleCommentOpenendInCommentedLine) {
    std::stringstream text{};
    text << "// /*" << "\n";
    text << "#include <foo.h>" << "\n";

    const auto result = extractIncludes(text);

    const std::set<std::string> expected = {"foo.h"};
    EXPECT_EQ(result, expected);
}

TEST(extractIncludes, FileWithComplexCases) {
    std::ifstream instream{"dwyu/aspect/private/preprocessing/test/data/commented_includes.h"};
    ASSERT_TRUE(instream.is_open());

    const auto result = extractIncludes(instream);

    const std::set<std::string> expected = {
        "include_a.h", "include_b.h", "include_c.h", "include_d.h", "include_e.h", "include_f.h", "include_g.h",
    };
    EXPECT_EQ(result, expected);
}

} // namespace dwyu
