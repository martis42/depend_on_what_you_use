#include "dwyu/private/program_options.h"

#include <gmock/gmock.h>
#include <gtest/gtest.h>
#include <string>
#include <vector>

namespace dwyu {

// Most efficient way to write the tests is by using C arrays to mimic the main() parameters
// NOLINTBEGIN(cppcoreguidelines-avoid-c-arrays, cppcoreguidelines-pro-bounds-array-to-pointer-decay)

TEST(ParsingSomeFlag, AnExistingFlagYieldsTrue) {
    bool flag{false};
    ProgramOptionsParser unit{};
    unit.addOptionFlag("--flag", flag);

    const int argc{2};
    ProgramOptionsParser::ConstCharArray argv = {"unrelated", "--flag"};
    unit.parseOptions(argc, argv);

    EXPECT_TRUE(flag);
}

TEST(ParsingSomeFlag, AMissingFlagYieldsFalse) {
    bool flag{true};
    std::vector<std::string> list{};
    ProgramOptionsParser unit{};
    unit.addOptionFlag("--flag", flag);
    unit.addOptionList("--list", list);

    const int argc{2};
    ProgramOptionsParser::ConstCharArray argv = {"unrelated", "--list"};
    unit.parseOptions(argc, argv);

    EXPECT_FALSE(flag);
}

TEST(ParsingSomeValue, ReadAGivenValue) {
    std::string value{};
    ProgramOptionsParser unit{};
    unit.addOptionValue("--value", value);

    const int argc{3};
    ProgramOptionsParser::ConstCharArray argv = {"unrelated", "--value", "foo"};
    unit.parseOptions(argc, argv);

    EXPECT_EQ(value, "foo");
}

TEST(ParsingSomeValue, FailOnNoValue) {
    bool flag{false};
    std::string value{};
    ProgramOptionsParser unit{};
    unit.addOptionFlag("--flag", flag);
    unit.addOptionValue("--value", value);

    // No value at all
    {
        const int argc{2};
        ProgramOptionsParser::ConstCharArray argv = {"unrelated", "--value"};
        EXPECT_EXIT(unit.parseOptions(argc, argv), testing::ExitedWithCode(1),
                    "Expected a value for the last option, but none was provided");
    }

    // Followed by other option
    {
        const int argc{3};
        ProgramOptionsParser::ConstCharArray argv = {"unrelated", "--value", "--flag"};
        EXPECT_EXIT(unit.parseOptions(argc, argv), testing::ExitedWithCode(1),
                    "Expected a value, but received another option: '--flag'");
    }
}

TEST(ParsingSomeValue, FailOnMultipleValues) {
    std::string value{};
    ProgramOptionsParser unit{};
    unit.addOptionValue("--value", value);

    const int argc{4};
    ProgramOptionsParser::ConstCharArray argv = {"unrelated", "--value", "foo", "bar"};
    EXPECT_EXIT(unit.parseOptions(argc, argv), testing::ExitedWithCode(1),
                "Got second value 'bar' for single value option '--value'");
}

TEST(ParsingSomeList, ReadGivenValues) {
    std::vector<std::string> list{};
    ProgramOptionsParser unit{};
    unit.addOptionList("--list", list);

    // Empty input
    {
        const int argc{2};
        ProgramOptionsParser::ConstCharArray argv = {"unrelated", "--list"};
        unit.parseOptions(argc, argv);

        EXPECT_TRUE(list.empty());
    }

    // Multiple values
    {
        const int argc{5};
        ProgramOptionsParser::ConstCharArray argv = {"unrelated", "--list", "x", "foo", "-bar"};
        unit.parseOptions(argc, argv);

        EXPECT_THAT(list, testing::ElementsAre("x", "foo", "-bar"));
    }
}

TEST(ParseMultipleOptions, ReadDifferentValues) {
    std::vector<std::string> list{};
    std::string value{};
    bool flag{false};

    ProgramOptionsParser unit{};
    unit.addOptionFlag("--flag", flag);
    unit.addOptionValue("--value", value);
    unit.addOptionList("--list", list);

    const int argc{7};
    ProgramOptionsParser::ConstCharArray argv = {"unrelated", "--list", "tik", "tok", "--value", "foo", "--flag"};
    unit.parseOptions(argc, argv);

    EXPECT_THAT(list, testing::ElementsAre("tik", "tok"));
    EXPECT_EQ(value, "foo");
    EXPECT_TRUE(flag);
}

TEST(ProgramOptionsParser, ExpectAtLeastOneOption) {
    ProgramOptionsParser unit{};

    const int argc = 1;
    ProgramOptionsParser::ConstCharArray argv = {"unrelated"};

    EXPECT_EXIT(unit.parseOptions(argc, argv), testing::ExitedWithCode(1),
                "At least a single option is expected to be present");
}

TEST(ProgramOptionsParser, ExpectAtLeastTwoCliArguments) {
    bool flag{false};
    ProgramOptionsParser unit{};
    unit.addOptionFlag("--flag", flag);

    const int argc = 1;
    ProgramOptionsParser::ConstCharArray argv = {"unrelated"};

    EXPECT_EXIT(unit.parseOptions(argc, argv), testing::ExitedWithCode(1), "Expecting at least 2 argv elements");
}

TEST(ProgramOptionsParser, FailOnUnexpectedOption) {
    std::string value{};
    ProgramOptionsParser unit{};
    unit.addOptionValue("--value", value);

    const int argc{2};
    ProgramOptionsParser::ConstCharArray argv = {"unrelated", "--other_value"};

    EXPECT_EXIT(unit.parseOptions(argc, argv), testing::ExitedWithCode(1), "Received invalid option: '--other_value'");
}

TEST(ProgramOptionsParser, FailOnUnexpectedExtraContent) {
    bool flag{false};
    ProgramOptionsParser unit{};
    unit.addOptionFlag("--flag", flag);

    const int argc = 3;
    ProgramOptionsParser::ConstCharArray argv = {"unrelated", "--flag", "extra_input"};

    EXPECT_EXIT(unit.parseOptions(argc, argv), testing::ExitedWithCode(1),
                "Got a value without it being associated to an option: 'extra_input'");
}

TEST(ProgramOptionsParser, ReadOptionsFromParamFile) {
    std::vector<std::string> list{};
    std::string value{};
    bool flag{false};

    ProgramOptionsParser unit{};
    unit.addOptionList("--list", list);
    unit.addOptionValue("--value", value);
    unit.addOptionFlag("--flag", flag);

    const int argc{2};
    ProgramOptionsParser::ConstCharArray argv = {"unrelated",
                                                 "--param_file=dwyu/private/test/data/multiple_options.txt"};
    unit.parseOptions(argc, argv);

    ASSERT_EQ(list.size(), 2);
    EXPECT_EQ(list[0], "tik");
    EXPECT_EQ(list[1], "tok");
    EXPECT_EQ(value, "foo");
    EXPECT_TRUE(flag);
}

TEST(ProgramOptionsParser, FailOnNotExistingParamFile) {
    bool flag{false};
    ProgramOptionsParser unit{};
    unit.addOptionFlag("--flag", flag);

    const int argc{2};
    ProgramOptionsParser::ConstCharArray argv = {"unrelated", "--param_file=not/existing/path"};

    EXPECT_EXIT(unit.parseOptions(argc, argv), testing::ExitedWithCode(1),
                "Could not open param_file 'not/existing/path'");
}

// NOLINTEND(cppcoreguidelines-avoid-c-arrays, cppcoreguidelines-pro-bounds-array-to-pointer-decay)

} // namespace dwyu
