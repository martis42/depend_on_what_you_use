#include "dwyu/private/program_options.h"

#include <gmock/gmock.h>
#include <gtest/gtest.h>
#include <string>
#include <vector>

namespace dwyu {
namespace {

void parseOptions(std::vector<const char*> args, ProgramOptionsParser& parser) {
    args.insert(args.begin(), "program_name");
    parser.parseOptions(static_cast<int>(args.size()), args.data());
}

TEST(ParsingSomeFlag, AnExistingFlagYieldsTrue) {
    bool flag{false};
    ProgramOptionsParser unit{};
    unit.addOptionFlag("--flag", flag);

    parseOptions({"--flag"}, unit);

    EXPECT_TRUE(flag);
}

TEST(ParsingSomeFlag, AMissingFlagYieldsFalse) {
    bool flag{true};
    ProgramOptionsParser unit{};
    unit.addOptionFlag("--flag", flag);

    parseOptions({}, unit);

    EXPECT_FALSE(flag);
}

TEST(ParsingSomeFlag, FailforValueAfterFlag) {
    bool flag{false};
    ProgramOptionsParser unit{};
    unit.addOptionFlag("--flag", flag);

    EXPECT_EXIT(parseOptions({"--flag", "extra_input"}, unit), testing::ExitedWithCode(1),
                "Got a value without it being associated to an option: 'extra_input'");
}

TEST(ParsingSomeValue, ReadAGivenValue) {
    std::string value{};
    ProgramOptionsParser unit{};
    unit.addOptionValue("--value", value);

    parseOptions({"--value", "foo"}, unit);

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
        EXPECT_EXIT(parseOptions({"--value"}, unit), testing::ExitedWithCode(1),
                    "Expected a value for the last option, but none was provided");
    }

    // Followed by other option
    {
        EXPECT_EXIT(parseOptions({"--value", "--flag"}, unit), testing::ExitedWithCode(1),
                    "Expected a value, but received another option: '--flag'");
    }
}

TEST(ParsingSomeValue, FailOnMultipleValues) {
    std::string value{};
    ProgramOptionsParser unit{};
    unit.addOptionValue("--value", value);

    EXPECT_EXIT(parseOptions({"--value", "foo", "bar"}, unit), testing::ExitedWithCode(1),
                "Got second value 'bar' for single value option '--value'");
}

TEST(ParsingSomeList, ReadGivenValues) {
    std::vector<std::string> list{};
    ProgramOptionsParser unit{};
    unit.addOptionList("--list", list);

    // No input
    { EXPECT_TRUE(list.empty()); }

    // Empty input
    {
        parseOptions({"--list"}, unit);

        EXPECT_TRUE(list.empty());
    }

    // Multiple values
    {
        parseOptions({"--list", "x", "foo", "-bar"}, unit);

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

    parseOptions({"--list", "tik", "tok", "--value", "foo", "--flag"}, unit);

    EXPECT_THAT(list, testing::ElementsAre("tik", "tok"));
    EXPECT_EQ(value, "foo");
    EXPECT_TRUE(flag);
}

TEST(ProgramOptionsParser, FailOnNoArgumentsForValueOption) {
    std::string value{};
    ProgramOptionsParser unit{};
    unit.addOptionValue("--value", value);

    EXPECT_EXIT(parseOptions({}, unit), testing::ExitedWithCode(1),
                "No arguments provided and at least one value option is requested");
}

TEST(ProgramOptionsParser, FailOnUnexpectedOption) {
    // Expected no option at all
    {
        ProgramOptionsParser unit{};

        EXPECT_EXIT(parseOptions({"--some_option"}, unit), testing::ExitedWithCode(1),
                    "Received invalid option: '--some_option'");
    }

    // Expected other option
    {
        std::string value{};
        ProgramOptionsParser unit{};
        unit.addOptionValue("--value", value);

        EXPECT_EXIT(parseOptions({"--other_value"}, unit), testing::ExitedWithCode(1),
                    "Received invalid option: '--other_value'");
    }
}

TEST(ProgramOptionsParser, FailOnUnexpectedExtraContent) {
    ProgramOptionsParser unit{};

    EXPECT_EXIT(parseOptions({"random_input"}, unit), testing::ExitedWithCode(1),
                "Got a value without it being associated to an option: 'random_input'");
}

TEST(ProgramOptionsParser, ReadOptionsFromParamFile) {
    std::vector<std::string> list{};
    std::string value{};
    bool flag{false};

    ProgramOptionsParser unit{};
    unit.addOptionList("--list", list);
    unit.addOptionValue("--value", value);
    unit.addOptionFlag("--flag", flag);

    parseOptions({"--param_file=dwyu/private/test/data/multiple_options.txt"}, unit);

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

    EXPECT_EXIT(parseOptions({"--param_file=not/existing/path"}, unit), testing::ExitedWithCode(1),
                "Could not open param_file 'not/existing/path'");
}

} // namespace
} // namespace dwyu
