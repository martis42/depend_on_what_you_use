#include "dwyu/aspect/private/analyze_includes/utility.h"

#include <gmock/gmock.h>
#include <gtest/gtest.h>

#include <stdexcept>
#include <tuple>

namespace dwyu {
namespace {

TEST(ReadJsonFromFile, ThrowOnMissingFile) {
    EXPECT_THAT(
        []() { std::ignore = readJsonFromFile("null"); },
        testing::ThrowsMessage<std::invalid_argument>(testing::HasSubstr("Provided file does not exist: null")));
}

TEST(ReadJsonFromFile, ReturnEmptyOnMissingFileWhenIgnoringMissingFiles) {
    constexpr bool no_error_on_missing_file = true;
    const auto result = readJsonFromFile("null", no_error_on_missing_file);
    EXPECT_EQ(result, nlohmann::json{});
}

TEST(ReadJsonFromFile, ReadData) {
    const auto result =
        readJsonFromFile("dwyu/aspect/private/analyze_includes/test/data/cc/target_under_inspection.json");

    EXPECT_EQ(result.size(), 2);
    EXPECT_EQ(result["target"], "//:bar");
    EXPECT_THAT(result["header_files"], testing::ElementsAre("some/hdr_1.h", "some/hdr_2.h"));
}

} // namespace
} // namespace dwyu
