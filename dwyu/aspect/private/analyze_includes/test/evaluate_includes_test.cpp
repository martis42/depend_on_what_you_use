#include "dwyu/aspect/private/analyze_includes/evaluate_includes.h"
#include "dwyu/aspect/private/analyze_includes/include_statement.h"
#include "dwyu/aspect/private/analyze_includes/system_under_inspection.h"

#include <gmock/gmock.h>
#include <gtest/gtest.h>
#include <nlohmann/json.hpp>

#include <memory>
#include <string>
#include <vector>

namespace dwyu {
namespace {

std::vector<std::string> getMapKeys(const nlohmann::json& map) {
    std::vector<std::string> keys{};
    for (const auto& map_pair : map.items()) {
        keys.push_back(map_pair.key());
    }
    return keys;
}

TEST(EvaluateIncludes, SuccessForNoInput) {
    const std::vector<IncludeStatement> pub_includes{};
    const std::vector<IncludeStatement> priv_includes{};
    const SystemUnderInspection::HeadersToDepsMap pub_deps{};
    const SystemUnderInspection::HeadersToDepsMap all_deps{};
    SystemUnderInspection system_under_inspection{CcTargetUnderInspection{"//:foo", {}}, pub_deps, all_deps};
    const bool optimize_impl_deps = false;

    const auto result = evaluateIncludes(pub_includes, priv_includes, system_under_inspection, optimize_impl_deps);

    EXPECT_TRUE(result.isOk());

    const auto json_result = result.toJson();
    EXPECT_EQ(json_result["analyzed_target"].get<std::string>(), "//:foo");
    EXPECT_TRUE(json_result["public_includes_without_dep"].empty());
    EXPECT_TRUE(json_result["private_includes_without_dep"].empty());
    EXPECT_TRUE(json_result["unused_deps"].empty());
    EXPECT_TRUE(json_result["unused_implementation_deps"].empty());
    EXPECT_TRUE(json_result["deps_which_should_be_private"].empty());
    EXPECT_FALSE(json_result["use_implementation_deps"].get<bool>());
}

TEST(EvaluateIncludes, SuccessForAllChecks) {
    const std::vector<IncludeStatement> pub_includes{
        IncludeStatement{"pub_file_using_a.h", "<hdr_a.h>", "path/hdr_a.h"}};
    const std::vector<IncludeStatement> priv_includes{
        IncludeStatement{"priv_file_using_b.h", "<hdr_b.h>", "path/hdr_b.h"}};
    const auto pub_dep_a = std::make_shared<CcDependency>(CcDependency{"//pub/dep:a", {}});
    const auto priv_dep_b = std::make_shared<CcDependency>(CcDependency{"//priv/dep:b", {}});
    const SystemUnderInspection::HeadersToDepsMap pub_deps{{"path/hdr_a.h", {pub_dep_a}}};
    const SystemUnderInspection::HeadersToDepsMap all_deps{{"path/hdr_a.h", {pub_dep_a}},
                                                           {"path/hdr_b.h", {priv_dep_b}}};
    SystemUnderInspection system_under_inspection{CcTargetUnderInspection{"//:foo", {}}, pub_deps, all_deps};
    const bool optimize_impl_deps = true;

    const auto result = evaluateIncludes(pub_includes, priv_includes, system_under_inspection, optimize_impl_deps);

    EXPECT_TRUE(result.isOk());

    const auto json_result = result.toJson();
    EXPECT_EQ(json_result["analyzed_target"].get<std::string>(), "//:foo");
    EXPECT_TRUE(json_result["public_includes_without_dep"].empty());
    EXPECT_TRUE(json_result["private_includes_without_dep"].empty());
    EXPECT_TRUE(json_result["unused_deps"].empty());
    EXPECT_TRUE(json_result["unused_implementation_deps"].empty());
    EXPECT_TRUE(json_result["deps_which_should_be_private"].empty());
    EXPECT_TRUE(json_result["use_implementation_deps"].get<bool>());
}

TEST(EvaluateIncludes, DetectIncludesWithoutMatchingDependency) {
    const std::vector<IncludeStatement> pub_includes{
        IncludeStatement{"pub_file_using_a.h", "<pub_hdr_a_1.h>", "path/pub_hdr_a_1.h"},
        IncludeStatement{"pub_file_using_a.h", "<pub_hdr_a_2.h>", "path/pub_hdr_a_2.h"},
        IncludeStatement{"pub_file_using_b.h", "<pub_hdr_b.h>", "path/pub_hdr_b.h"},
        IncludeStatement{"pub_file_using_c.h", "<pub_hdr_c.h>", "path/pub_hdr_c.h"}};
    const std::vector<IncludeStatement> priv_includes{
        IncludeStatement{"priv_file_using_a.h", "<priv_hdr_a_1.h>", "path/priv_hdr_a_1.h"},
        IncludeStatement{"priv_file_using_a.h", "<priv_hdr_a_2.h>", "path/priv_hdr_a_2.h"},
        IncludeStatement{"priv_file_using_b.h", "<priv_hdr_b.h>", "path/priv_hdr_b.h"},
        IncludeStatement{"priv_file_using_c.h", "<priv_hdr_c.h>", "path/priv_hdr_c.h"}};
    const SystemUnderInspection::HeadersToDepsMap pub_deps{
        {"path/pub_hdr_b.h", {std::make_shared<CcDependency>(CcDependency{"//pub/dep:b", {}})}}};
    const SystemUnderInspection::HeadersToDepsMap all_deps{
        {"path/priv_hdr_b.h", {std::make_shared<CcDependency>(CcDependency{"//priv/dep:b", {}})}}};
    SystemUnderInspection system_under_inspection{CcTargetUnderInspection{"//:foo", {}}, pub_deps, all_deps};
    const bool optimize_impl_deps = false;

    const auto result = evaluateIncludes(pub_includes, priv_includes, system_under_inspection, optimize_impl_deps);

    EXPECT_FALSE(result.isOk());

    const auto json_result = result.toJson();
    EXPECT_EQ(json_result["analyzed_target"].get<std::string>(), "//:foo");
    EXPECT_TRUE(json_result["unused_deps"].empty());
    EXPECT_TRUE(json_result["unused_implementation_deps"].empty());
    EXPECT_TRUE(json_result["deps_which_should_be_private"].empty());
    EXPECT_FALSE(json_result["use_implementation_deps"].get<bool>());

    ASSERT_THAT(getMapKeys(json_result["public_includes_without_dep"]),
                testing::UnorderedElementsAre("pub_file_using_a.h", "pub_file_using_c.h"));
    EXPECT_THAT(json_result["public_includes_without_dep"]["pub_file_using_a.h"].get<std::vector<std::string>>(),
                testing::UnorderedElementsAre("pub_hdr_a_1.h", "pub_hdr_a_2.h"));
    EXPECT_THAT(json_result["public_includes_without_dep"]["pub_file_using_c.h"].get<std::vector<std::string>>(),
                testing::UnorderedElementsAre("pub_hdr_c.h"));

    ASSERT_THAT(getMapKeys(json_result["private_includes_without_dep"]),
                testing::UnorderedElementsAre("priv_file_using_a.h", "priv_file_using_c.h"));
    EXPECT_THAT(json_result["private_includes_without_dep"]["priv_file_using_a.h"].get<std::vector<std::string>>(),
                testing::UnorderedElementsAre("priv_hdr_a_1.h", "priv_hdr_a_2.h"));
    EXPECT_THAT(json_result["private_includes_without_dep"]["priv_file_using_c.h"].get<std::vector<std::string>>(),
                testing::UnorderedElementsAre("priv_hdr_c.h"));
}

TEST(EvaluateIncludes, DetectTheTargetUnderInspectionProvidingTheHeaders) {
    const std::vector<IncludeStatement> pub_includes{
        IncludeStatement{"pub_file_using_a.h", "<hdr_a.h>", "path/hdr_a.h"}};
    const std::vector<IncludeStatement> priv_includes{
        IncludeStatement{"priv_file_using_b.cpp", "<hdr_b.h>", "path/hdr_b.h"}};
    const SystemUnderInspection::HeadersToDepsMap pub_deps{};
    const SystemUnderInspection::HeadersToDepsMap all_deps{};
    SystemUnderInspection system_under_inspection{CcTargetUnderInspection{"//:foo", {"path/hdr_a.h", "path/hdr_b.h"}},
                                                  pub_deps, all_deps};
    const bool optimize_impl_deps = true;

    const auto result = evaluateIncludes(pub_includes, priv_includes, system_under_inspection, optimize_impl_deps);

    EXPECT_TRUE(result.isOk());

    const auto json_result = result.toJson();
    EXPECT_EQ(json_result["analyzed_target"].get<std::string>(), "//:foo");
    EXPECT_TRUE(json_result["public_includes_without_dep"].empty());
    EXPECT_TRUE(json_result["private_includes_without_dep"].empty());
    EXPECT_TRUE(json_result["unused_deps"].empty());
    EXPECT_TRUE(json_result["unused_implementation_deps"].empty());
    EXPECT_TRUE(json_result["deps_which_should_be_private"].empty());
    EXPECT_TRUE(json_result["use_implementation_deps"].get<bool>());
}

TEST(EvaluateIncludes, DetectUnusedDependencies) {
    const std::vector<IncludeStatement> pub_includes{};
    const std::vector<IncludeStatement> priv_includes{};
    const SystemUnderInspection::HeadersToDepsMap pub_deps{
        {"path/hdr_a.h", {std::make_shared<CcDependency>(CcDependency{"//pub/dep:a", {}})}},
        {"path/hdr_b.h", {std::make_shared<CcDependency>(CcDependency{"//pub/dep:b", {}})}}};
    const SystemUnderInspection::HeadersToDepsMap all_deps{
        {"path/hdr_a.h", {std::make_shared<CcDependency>(CcDependency{"//priv/dep:a", {}})}},
        {"path/hdr_b.h", {std::make_shared<CcDependency>(CcDependency{"//priv/dep:b", {}})}}};
    SystemUnderInspection system_under_inspection{CcTargetUnderInspection{"//:foo", {}}, pub_deps, all_deps};
    const bool optimize_impl_deps = false;

    const auto result = evaluateIncludes(pub_includes, priv_includes, system_under_inspection, optimize_impl_deps);

    EXPECT_FALSE(result.isOk());

    const auto json_result = result.toJson();
    EXPECT_EQ(json_result["analyzed_target"].get<std::string>(), "//:foo");
    EXPECT_TRUE(json_result["public_includes_without_dep"].empty());
    EXPECT_TRUE(json_result["private_includes_without_dep"].empty());
    EXPECT_THAT(json_result["unused_deps"].get<std::vector<std::string>>(),
                testing::UnorderedElementsAre("//pub/dep:a", "//pub/dep:b"));
    EXPECT_THAT(json_result["unused_implementation_deps"].get<std::vector<std::string>>(),
                testing::UnorderedElementsAre("//priv/dep:a", "//priv/dep:b"));
    EXPECT_TRUE(json_result["deps_which_should_be_private"].empty());
    EXPECT_FALSE(json_result["use_implementation_deps"].get<bool>());
}

TEST(EvaluateIncludes, UsingASingleHeaderIsSufficientToMarkADependencyAsUsed) {
    const std::vector<IncludeStatement> pub_includes{
        IncludeStatement{"pub_file_using_a.h", "<hdr_a_1.h>", "path/hdr_a_1.h"}};
    const std::vector<IncludeStatement> priv_includes{
        IncludeStatement{"priv_file_using_b.cpp", "<hdr_b_1.h>", "path/hdr_b_1.h"}};
    const auto pub_a = std::make_shared<CcDependency>(CcDependency{"//pub/dep:a", {}});
    const SystemUnderInspection::HeadersToDepsMap pub_deps{{"path/hdr_a_1.h", {pub_a}}, {"path/hdr_a_2.h", {pub_a}}};
    const auto priv_b = std::make_shared<CcDependency>(CcDependency{"//priv/dep:b", {}});
    const SystemUnderInspection::HeadersToDepsMap all_deps{{"path/hdr_b_1.h", {priv_b}}, {"path/hdr_b_2.h", {priv_b}}};
    SystemUnderInspection system_under_inspection{CcTargetUnderInspection{"//:foo", {}}, pub_deps, all_deps};
    const bool optimize_impl_deps = false;

    const auto result = evaluateIncludes(pub_includes, priv_includes, system_under_inspection, optimize_impl_deps);

    EXPECT_TRUE(result.isOk());

    const auto json_result = result.toJson();
    EXPECT_EQ(json_result["analyzed_target"].get<std::string>(), "//:foo");
    EXPECT_TRUE(json_result["public_includes_without_dep"].empty());
    EXPECT_TRUE(json_result["private_includes_without_dep"].empty());
    EXPECT_TRUE(json_result["unused_deps"].empty());
    EXPECT_TRUE(json_result["unused_implementation_deps"].empty());
    EXPECT_TRUE(json_result["deps_which_should_be_private"].empty());
    EXPECT_FALSE(json_result["use_implementation_deps"].get<bool>());
}

TEST(EvaluateIncludes, UsingAHeaderMarksAllAssociatedDependenciesAsUsed) {
    const std::vector<IncludeStatement> pub_includes{
        IncludeStatement{"pub_file_using_a.h", "<hdr_a.h>", "path/hdr_a.h"}};
    const std::vector<IncludeStatement> priv_includes{
        IncludeStatement{"riv_file_using_b.cpp", "<hdr_b.h>", "path/hdr_b.h"}};
    const SystemUnderInspection::HeadersToDepsMap pub_deps{
        {"path/hdr_a.h",
         {std::make_shared<CcDependency>(CcDependency{"//pub/dep:a_1", {}}),
          std::make_shared<CcDependency>(CcDependency{"//pub/dep:a_2", {}})}}};
    const SystemUnderInspection::HeadersToDepsMap all_deps{
        {"path/hdr_b.h",
         {std::make_shared<CcDependency>(CcDependency{"//priv/dep:b_1", {}}),
          std::make_shared<CcDependency>(CcDependency{"//priv/dep:b_2", {}})}}};
    SystemUnderInspection system_under_inspection{CcTargetUnderInspection{"//:foo", {}}, pub_deps, all_deps};
    const bool optimize_impl_deps = false;

    const auto result = evaluateIncludes(pub_includes, priv_includes, system_under_inspection, optimize_impl_deps);

    EXPECT_TRUE(result.isOk());

    const auto json_result = result.toJson();
    EXPECT_EQ(json_result["analyzed_target"].get<std::string>(), "//:foo");
    EXPECT_TRUE(json_result["public_includes_without_dep"].empty());
    EXPECT_TRUE(json_result["private_includes_without_dep"].empty());
    EXPECT_TRUE(json_result["unused_deps"].empty());
    EXPECT_TRUE(json_result["unused_implementation_deps"].empty());
    EXPECT_TRUE(json_result["deps_which_should_be_private"].empty());
    EXPECT_FALSE(json_result["use_implementation_deps"].get<bool>());
}

TEST(EvaluateIncludes, DetectDepsWhichShouldBePrivate) {
    const std::vector<IncludeStatement> pub_includes{};
    const std::vector<IncludeStatement> priv_includes{
        IncludeStatement{"priv_file_using_a.cpp", "<hdr_a.h>", "path/hdr_a.h"},
        IncludeStatement{"priv_file_using_b.cpp", "<hdr_b.h>", "path/hdr_b.h"}};
    const auto pub_a = std::make_shared<CcDependency>(CcDependency{"//pub/dep:a", {}});
    const auto pub_b = std::make_shared<CcDependency>(CcDependency{"//pub/dep:b", {}});
    const SystemUnderInspection::HeadersToDepsMap pub_deps{{"path/hdr_a.h", {pub_a}}, {"path/hdr_b.h", {pub_b}}};
    const SystemUnderInspection::HeadersToDepsMap all_deps{{"path/hdr_a.h", {pub_a}}, {"path/hdr_b.h", {pub_b}}};
    SystemUnderInspection system_under_inspection{CcTargetUnderInspection{"//:foo", {}}, pub_deps, all_deps};
    const bool optimize_impl_deps = true;

    const auto result = evaluateIncludes(pub_includes, priv_includes, system_under_inspection, optimize_impl_deps);

    EXPECT_FALSE(result.isOk());

    const auto json_result = result.toJson();
    EXPECT_EQ(json_result["analyzed_target"].get<std::string>(), "//:foo");
    EXPECT_TRUE(json_result["public_includes_without_dep"].empty());
    EXPECT_TRUE(json_result["private_includes_without_dep"].empty());
    EXPECT_TRUE(json_result["unused_deps"].empty());
    EXPECT_TRUE(json_result["unused_implementation_deps"].empty());
    EXPECT_THAT(json_result["deps_which_should_be_private"].get<std::vector<std::string>>(),
                testing::UnorderedElementsAre("//pub/dep:a", "//pub/dep:b"));
    EXPECT_TRUE(json_result["use_implementation_deps"].get<bool>());
}

TEST(EvaluateIncludes, ReportUniqueResultsForDepsWhichShouldBePrivate) {
    const std::vector<IncludeStatement> pub_includes{};
    const std::vector<IncludeStatement> priv_includes{
        IncludeStatement{"priv_file_using_a.cpp", "<hdr_a_1.h>", "path/hdr_a_1.h"},
        IncludeStatement{"priv_file_using_a.cpp", "<hdr_a_2.h>", "path/hdr_a_2.h"}};
    const auto pub_a = std::make_shared<CcDependency>(CcDependency{"//pub/dep:a", {}});
    const SystemUnderInspection::HeadersToDepsMap pub_deps{{"path/hdr_a_1.h", {pub_a}}, {"path/hdr_a_2.h", {pub_a}}};
    const SystemUnderInspection::HeadersToDepsMap all_deps{{"path/hdr_a_1.h", {pub_a}}, {"path/hdr_a_2.h", {pub_a}}};
    SystemUnderInspection system_under_inspection{CcTargetUnderInspection{"//:foo", {}}, pub_deps, all_deps};
    const bool optimize_impl_deps = true;

    const auto result = evaluateIncludes(pub_includes, priv_includes, system_under_inspection, optimize_impl_deps);

    EXPECT_FALSE(result.isOk());

    const auto json_result = result.toJson();
    EXPECT_EQ(json_result["analyzed_target"].get<std::string>(), "//:foo");
    EXPECT_TRUE(json_result["public_includes_without_dep"].empty());
    EXPECT_TRUE(json_result["private_includes_without_dep"].empty());
    EXPECT_TRUE(json_result["unused_deps"].empty());
    EXPECT_TRUE(json_result["unused_implementation_deps"].empty());
    EXPECT_THAT(json_result["deps_which_should_be_private"].get<std::vector<std::string>>(),
                testing::UnorderedElementsAre("//pub/dep:a"));
    EXPECT_TRUE(json_result["use_implementation_deps"].get<bool>());
}

TEST(EvaluateIncludes, ReportUniqueResultsForAllUnusedDepsErrors) {
    const std::vector<IncludeStatement> pub_includes{};
    const std::vector<IncludeStatement> priv_includes{};
    const auto pub_a = std::make_shared<CcDependency>(CcDependency{"//pub/dep:a", {}});
    const auto priv_b = std::make_shared<CcDependency>(CcDependency{"//priv/dep:b", {}});
    const SystemUnderInspection::HeadersToDepsMap pub_deps{{"path/hdr_a_1.h", {pub_a}}, {"path/hdr_a_2.h", {pub_a}}};
    const SystemUnderInspection::HeadersToDepsMap all_deps{{"path/hdr_b_1.h", {priv_b}}, {"path/hdr_b_2.h", {priv_b}}};
    SystemUnderInspection system_under_inspection{CcTargetUnderInspection{"//:foo", {}}, pub_deps, all_deps};
    const bool optimize_impl_deps = true;

    const auto result = evaluateIncludes(pub_includes, priv_includes, system_under_inspection, optimize_impl_deps);

    EXPECT_FALSE(result.isOk());

    const auto json_result = result.toJson();
    EXPECT_EQ(json_result["analyzed_target"].get<std::string>(), "//:foo");
    EXPECT_TRUE(json_result["public_includes_without_dep"].empty());
    EXPECT_TRUE(json_result["private_includes_without_dep"].empty());
    EXPECT_THAT(json_result["unused_deps"].get<std::vector<std::string>>(),
                testing::UnorderedElementsAre("//pub/dep:a"));
    EXPECT_THAT(json_result["unused_implementation_deps"].get<std::vector<std::string>>(),
                testing::UnorderedElementsAre("//priv/dep:b"));
    EXPECT_TRUE(json_result["deps_which_should_be_private"].empty());
    EXPECT_TRUE(json_result["use_implementation_deps"].get<bool>());
}

} // namespace
} // namespace dwyu
