#include "dwyu/private/program_options.h"

#include <gtest/gtest.h>
#include <string>
#include <vector>

namespace dwyu {

TEST(ProgramOptionsParser, ParseFlag_ExistingFlagYieldsTrue) {
    bool flag{false};
    ProgramOptionsParser unit{};
    unit.addOptionFlag("--flag", flag);

    const int argc{2};
    const char* argv[] = {"unrelated", "--flag"};
    unit.parseOptions(argc, argv);

    EXPECT_TRUE(flag);
}

TEST(ProgramOptionsParser, ParseFlag_MissingFlagYieldsFalse) {
    bool flag{true};
    std::vector<std::string> list{};
    ProgramOptionsParser unit{};
    unit.addOptionFlag("--flag", flag);
    unit.addOptionList("--list", list);

    const int argc{2};
    const char* argv[] = {"unrelated", "--list"};
    unit.parseOptions(argc, argv);

    EXPECT_FALSE(flag);
}

TEST(ProgramOptionsParser, ParseValue_ReadValue) {
    std::string value{};
    ProgramOptionsParser unit{};
    unit.addOptionValue("--value", value);

    const int argc{3};
    const char* argv[] = {"unrelated", "--value", "foo"};
    unit.parseOptions(argc, argv);

    EXPECT_EQ(value, "foo");
}

TEST(ProgramOptionsParser, ParseValue_FailOnNoValue) {
    bool flag{false};
    std::string value{"default"};
    ProgramOptionsParser unit{};
    unit.addOptionFlag("--flag", flag);
    unit.addOptionValue("--value", value);

    // No value at all
    {
        const int argc{2};
        const char* argv[] = {"unrelated", "--value"};
        unit.parseOptions(argc, argv);
        EXPECT_EQ(value, "default");
    }

    // Followed by other option
    {
        const int argc{3};
        const char* argv[] = {"unrelated", "--value", "--flag"};
        unit.parseOptions(argc, argv);
        EXPECT_EQ(value, "default");
    }
}

TEST(ProgramOptionsParser, ParseList_ReadValue) {
    std::vector<std::string> list{};
    ProgramOptionsParser unit{};
    unit.addOptionList("--list", list);

    // Empty input
    {
        const int argc{2};
        const char* argv[] = {"unrelated", "--list"};
        unit.parseOptions(argc, argv);

        EXPECT_TRUE(list.empty());
    }

    // Multiple values
    {
        const int argc{4};
        const char* argv[] = {"unrelated", "--list", "foo", "bar"};
        unit.parseOptions(argc, argv);

        ASSERT_EQ(list.size(), 2);
        EXPECT_EQ(list[0], "foo");
        EXPECT_EQ(list[1], "bar");
    }
}

TEST(ProgramOptionsParser, Parsing_MultipleOptions) {
    std::vector<std::string> list{};
    std::string value{};
    bool flag{false};

    ProgramOptionsParser unit{};
    unit.addOptionFlag("--flag", flag);
    unit.addOptionValue("--value", value);
    unit.addOptionList("--list", list);

    const int argc{7};
    const char* argv[] = {"unrelated", "--list", "tik", "tok", "--value", "foo", "--flag"};
    unit.parseOptions(argc, argv);

    ASSERT_EQ(list.size(), 2);
    EXPECT_EQ(list[0], "tik");
    EXPECT_EQ(list[1], "tok");
    EXPECT_EQ(value, "foo");
    EXPECT_TRUE(flag);
}

TEST(ProgramOptionsParser, Parsing_ExpectAtLeastOneOption) {
    ProgramOptionsParser unit{};

    const int argc = 0;
    const char* argv[] = {};

    EXPECT_EXIT(unit.parseOptions(argc, argv), testing::ExitedWithCode(1),
                "At least a single option is expected to be present");
}

TEST(ProgramOptionsParser, Parsing_ExpectAtLeastTwoCliArguments) {
    bool flag{false};
    ProgramOptionsParser unit{};
    unit.addOptionFlag("--flag", flag);

    const int argc = 1;
    const char* argv[] = {"unrelated"};

    EXPECT_EXIT(unit.parseOptions(argc, argv), testing::ExitedWithCode(1), "Expecting at least 2 argv elements");
}

TEST(ProgramOptionsParser, Parse_FailOnUnexpectedOption) {
    std::string value{};
    ProgramOptionsParser unit{};
    unit.addOptionValue("--value", value);

    const int argc{2};
    const char* argv[] = {"unrelated", "--other_value"};

    EXPECT_EXIT(unit.parseOptions(argc, argv), testing::ExitedWithCode(1), "Received invalid option: '--other_value'");
}

TEST(ProgramOptionsParser, Parsing_FailOnUnexpectedExtraContent) {
    bool flag{false};
    ProgramOptionsParser unit{};
    unit.addOptionFlag("--flag", flag);

    const int argc = 3;
    const char* argv[] = {"unrelated", "--flag", "extra_input"};

    EXPECT_EXIT(unit.parseOptions(argc, argv), testing::ExitedWithCode(1),
                "Got a value without it being associated to an option: 'extra_input'");
}

TEST(ProgramOptionsParser, ParamFile_ReadOptionsFromFile) {
    std::vector<std::string> list{};
    std::string value{};
    bool flag{false};

    ProgramOptionsParser unit{};
    unit.addOptionList("--list", list);
    unit.addOptionValue("--value", value);
    unit.addOptionFlag("--flag", flag);

    const int argc{2};
    const char* argv[] = {"unrelated", "--param_file=dwyu/private/test/data/multiple_options.txt"};
    unit.parseOptions(argc, argv);

    ASSERT_EQ(list.size(), 2);
    EXPECT_EQ(list[0], "tik");
    EXPECT_EQ(list[1], "tok");
    EXPECT_EQ(value, "foo");
    EXPECT_TRUE(flag);
}

TEST(ProgramOptionsParser, ParamFile_FailOnMissingParamFile) {
    bool flag{false};
    ProgramOptionsParser unit{};
    unit.addOptionFlag("--flag", flag);

    const int argc{2};
    const char* argv[] = {"unrelated", "--param_file=not/existing/path"};

    EXPECT_EXIT(unit.parseOptions(argc, argv), testing::ExitedWithCode(1),
                "Could not open param_file 'not/existing/path'");
}

} // namespace dwyu
