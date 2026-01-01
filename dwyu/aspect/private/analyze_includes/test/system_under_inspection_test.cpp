#include "dwyu/aspect/private/analyze_includes/system_under_inspection.h"

#include <gmock/gmock.h>
#include <gtest/gtest.h>

#include <algorithm>
#include <memory>
#include <ostream>
#include <string>
#include <vector>

namespace dwyu {

// NOLINTNEXTLINE(misc-use-anonymous-namespace) Has to be in the namespace of the type
static void PrintTo(const dwyu::TargetUsage::Status& status, std::ostream* stream) {
    switch (status) {
    case dwyu::TargetUsage::Status::None:
        *stream << "None";
        break;
    case dwyu::TargetUsage::Status::Private:
        *stream << "Private";
        break;
    case dwyu::TargetUsage::Status::Public:
        *stream << "Public";
        break;
    default:
        *stream << "UNKNOWN_STATUS";
    }
}

namespace {

void checkForExpectedMapping(const SystemUnderInspection::HeadersToDepsMap& hdrs_to_deps_map,
                             const std::string& header_file,
                             const std::vector<std::string>& expected_deps) {
    const auto mapped_header_it = hdrs_to_deps_map.find(header_file);
    ASSERT_TRUE(mapped_header_it != hdrs_to_deps_map.end())
        << "Header file '" << header_file << "' not found in hdrs_to_deps_map";

    const auto& deps = mapped_header_it->second;
    for (const auto& expected_dep : expected_deps) {
        const auto dep_it =
            std::find_if(deps.begin(), deps.end(), [&expected_dep](const std::shared_ptr<CcDependency>& dep) {
                return dep == nullptr ? false : dep->name == expected_dep;
            });

        ASSERT_TRUE(dep_it != deps.end())
            << "Expected dependency '" << expected_dep << "' not found for header '" << header_file << "'";
        EXPECT_FALSE((*dep_it)->usage.is_used())
            << "Dependency '" << expected_dep << "' for header '" << header_file << "' is not unused";
    }
}

struct TargetUsageSpec {
    std::vector<TargetUsage::Status> updates;
    TargetUsage::Status expected_status;
};

class TargetUsageStateMachine : public testing::TestWithParam<TargetUsageSpec> {};

TEST_P(TargetUsageStateMachine, /* unused */) {
    TargetUsage unit{};
    const auto& spec = GetParam();

    for (const auto update : spec.updates) {
        unit.update(update);
    }

    EXPECT_TRUE(unit.is_used());
    EXPECT_EQ(unit.usage(), spec.expected_status);
}

INSTANTIATE_TEST_SUITE_P(
    /* unused */,
    TargetUsageStateMachine,
    testing::Values(
        // Single updates
        TargetUsageSpec{{TargetUsage::Status::Public}, TargetUsage::Status::Public},
        TargetUsageSpec{{TargetUsage::Status::Private}, TargetUsage::Status::Private},
        // Multiple updates
        TargetUsageSpec{{TargetUsage::Status::Public, TargetUsage::Status::Public}, TargetUsage::Status::Public},
        TargetUsageSpec{{TargetUsage::Status::Private, TargetUsage::Status::Private}, TargetUsage::Status::Private},
        TargetUsageSpec{{TargetUsage::Status::Public, TargetUsage::Status::Private}, TargetUsage::Status::Public},
        TargetUsageSpec{{TargetUsage::Status::Private, TargetUsage::Status::Public}, TargetUsage::Status::Public}));

TEST(TargetUsage, ByDefaultIsNotUsed) {
    const TargetUsage unit{};

    EXPECT_FALSE(unit.is_used());
    EXPECT_EQ(unit.usage(), TargetUsage::Status::None);
}

TEST(GetSystemUnderInspection, GivenTargetUnderInspectionReadAllDataCorrectly) {
    const auto system = getSystemUnderInspection(
        "dwyu/aspect/private/analyze_includes/test/data/cc/target_under_inspection.json", {}, {});

    const auto& tui = system.target_under_inspection;
    EXPECT_EQ(tui.name, "//:bar");
    ASSERT_THAT(tui.header_files, testing::UnorderedElementsAre("some/hdr_1.h", "some/hdr_2.h"));
}

TEST(GetSystemUnderInspection, GivenTargetUnderInspectionWithoutHeadersExpectData) {
    const auto system = getSystemUnderInspection(
        "dwyu/aspect/private/analyze_includes/test/data/cc/target_under_inspection_no_headers.json", {}, {});

    const auto& tui = system.target_under_inspection;
    EXPECT_EQ(tui.name, "//:foo");
    EXPECT_TRUE(tui.header_files.empty());
}

TEST(GetSystemUnderInspection, GivenNoDepsExpectEmptyMaps) {
    const auto system = getSystemUnderInspection(
        "dwyu/aspect/private/analyze_includes/test/data/cc/target_under_inspection.json", {}, {});

    EXPECT_TRUE(system.headers_to_public_deps_map.empty());
    EXPECT_TRUE(system.headers_to_all_deps_map.empty());
}

TEST(GetSystemUnderInspection, GivenDepsWithoutHeadersExpectEmptyMaps) {
    const auto system =
        getSystemUnderInspection("dwyu/aspect/private/analyze_includes/test/data/cc/target_under_inspection.json",
                                 {"dwyu/aspect/private/analyze_includes/test/data/cc/dep_info_no_headers.json"},
                                 {"dwyu/aspect/private/analyze_includes/test/data/cc/dep_info_no_headers.json"});

    EXPECT_TRUE(system.headers_to_public_deps_map.empty());
    EXPECT_TRUE(system.headers_to_all_deps_map.empty());
}

TEST(GetSystemUnderInspection, GivenDepsWithHeadersReadAndCombineThemCorrectly) {
    const auto system =
        getSystemUnderInspection("dwyu/aspect/private/analyze_includes/test/data/cc/target_under_inspection.json",
                                 {"dwyu/aspect/private/analyze_includes/test/data/cc/dep_info_foo.json",
                                  "dwyu/aspect/private/analyze_includes/test/data/cc/dep_info_foobar.json"},
                                 {"dwyu/aspect/private/analyze_includes/test/data/cc/impl_dep_info_fizz.json",
                                  "dwyu/aspect/private/analyze_includes/test/data/cc/impl_dep_info_buzz.json"});

    ASSERT_EQ(system.headers_to_public_deps_map.size(), 4);
    ASSERT_EQ(system.headers_to_all_deps_map.size(), 8);

    checkForExpectedMapping(system.headers_to_public_deps_map, "foo/hdr_1.h", {"//public:foo"});
    checkForExpectedMapping(system.headers_to_public_deps_map, "foo/hdr_2.h", {"//public:foo"});
    checkForExpectedMapping(system.headers_to_public_deps_map, "foobar/hdr_1.h", {"//public:foobar"});
    checkForExpectedMapping(system.headers_to_public_deps_map, "foobar/hdr_2.h", {"//public:foobar"});

    checkForExpectedMapping(system.headers_to_all_deps_map, "foo/hdr_1.h", {"//public:foo"});
    checkForExpectedMapping(system.headers_to_all_deps_map, "foo/hdr_2.h", {"//public:foo"});
    checkForExpectedMapping(system.headers_to_all_deps_map, "foobar/hdr_1.h", {"//public:foobar"});
    checkForExpectedMapping(system.headers_to_all_deps_map, "foobar/hdr_2.h", {"//public:foobar"});
    checkForExpectedMapping(system.headers_to_all_deps_map, "fizz/hdr_1.h", {"//private:fizz"});
    checkForExpectedMapping(system.headers_to_all_deps_map, "fizz/hdr_2.h", {"//private:fizz"});
    checkForExpectedMapping(system.headers_to_all_deps_map, "buzz/hdr_1.h", {"//private:buzz"});
    checkForExpectedMapping(system.headers_to_all_deps_map, "buzz/hdr_2.h", {"//private:buzz"});
}

TEST(GetSystemUnderInspection, GivenDuplicateHeadersFromDifferentDepsExpectMappingToCorrectDeps) {
    const auto system =
        getSystemUnderInspection("dwyu/aspect/private/analyze_includes/test/data/cc/target_under_inspection.json",
                                 {"dwyu/aspect/private/analyze_includes/test/data/cc/dep_info_duplicate_header_a.json",
                                  "dwyu/aspect/private/analyze_includes/test/data/cc/dep_info_duplicate_header_b.json"},
                                 {});

    EXPECT_EQ(system.headers_to_public_deps_map.size(), 3);
    EXPECT_EQ(system.headers_to_all_deps_map.size(), 3);

    checkForExpectedMapping(system.headers_to_public_deps_map, "unique_a.h", {"//:duplicate_header_a"});
    checkForExpectedMapping(system.headers_to_public_deps_map, "unique_b.h", {"//:duplicate_header_b"});
    checkForExpectedMapping(system.headers_to_public_deps_map, "duplicated.h",
                            {"//:duplicate_header_a", "//:duplicate_header_b"});

    checkForExpectedMapping(system.headers_to_all_deps_map, "unique_a.h", {"//:duplicate_header_a"});
    checkForExpectedMapping(system.headers_to_all_deps_map, "unique_b.h", {"//:duplicate_header_b"});
    checkForExpectedMapping(system.headers_to_all_deps_map, "duplicated.h",
                            {"//:duplicate_header_a", "//:duplicate_header_b"});
}

} // namespace
} // namespace dwyu
