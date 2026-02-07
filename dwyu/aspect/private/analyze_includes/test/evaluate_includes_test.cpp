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

// The "all dependencies" map should always include both public and private dependencies
SystemUnderInspection::HeadersToDepsMap makeAllDeps(const SystemUnderInspection::HeadersToDepsMap& pub_deps,
                                                    const SystemUnderInspection::HeadersToDepsMap& impl_deps) {
    auto all_deps{pub_deps};

    for (const auto& impl_depr : impl_deps) {
        const auto& hdr = impl_depr.first;
        const auto& deps = impl_depr.second;

        auto all_deps_hdr_match = all_deps.find(hdr);
        if (all_deps_hdr_match != all_deps.end()) {
            // Header is already present, add further dependencies associated with the header
            all_deps_hdr_match->second.insert(all_deps_hdr_match->second.end(), deps.begin(), deps.end());
            continue;
        }
        // Header is not present, add new entry
        all_deps[hdr] = deps;
    }

    return all_deps;
}

std::shared_ptr<CcDependency> makeDep(const std::string& name) {
    return std::make_shared<CcDependency>(CcDependency{name, {}});
}

TEST(EvaluateIncludes, SuccessForNoInput) {
    const std::vector<IncludeStatement> pub_includes{};
    const std::vector<IncludeStatement> priv_includes{};
    const SystemUnderInspection::HeadersToDepsMap pub_deps{};
    const auto all_deps = makeAllDeps(pub_deps, {});
    SystemUnderInspection system_under_inspection{CcTargetUnderInspection{"//:foo", {}}, pub_deps, all_deps};
    const bool report_missing_direct_deps = true;
    const bool report_unused_deps = true;
    const bool optimize_impl_deps = false;

    const auto result = evaluateIncludes(pub_includes, priv_includes, system_under_inspection,
                                         report_missing_direct_deps, report_unused_deps, optimize_impl_deps);

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
    const SystemUnderInspection::HeadersToDepsMap pub_deps{{"path/hdr_a.h", {makeDep("//pub/dep:a")}}};
    const auto all_deps = makeAllDeps(pub_deps, {{"path/hdr_b.h", {makeDep("//priv/dep:b")}}});

    SystemUnderInspection system_under_inspection{CcTargetUnderInspection{"//:foo", {}}, pub_deps, all_deps};
    const bool report_missing_direct_deps = true;
    const bool report_unused_deps = true;
    const bool optimize_impl_deps = true;

    const auto result = evaluateIncludes(pub_includes, priv_includes, system_under_inspection,
                                         report_missing_direct_deps, report_unused_deps, optimize_impl_deps);

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
    const SystemUnderInspection::HeadersToDepsMap pub_deps{{"path/pub_hdr_b.h", {makeDep("//pub/dep:b")}}};
    const auto all_deps = makeAllDeps(pub_deps, {{"path/priv_hdr_b.h", {makeDep("//priv/dep:b")}}});

    SystemUnderInspection system_under_inspection{CcTargetUnderInspection{"//:foo", {}}, pub_deps, all_deps};
    const bool report_missing_direct_deps = true;
    const bool report_unused_deps = true;
    const bool optimize_impl_deps = false;

    const auto result = evaluateIncludes(pub_includes, priv_includes, system_under_inspection,
                                         report_missing_direct_deps, report_unused_deps, optimize_impl_deps);

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
    const auto all_deps = makeAllDeps(pub_deps, {});
    SystemUnderInspection system_under_inspection{CcTargetUnderInspection{"//:foo", {"path/hdr_a.h", "path/hdr_b.h"}},
                                                  pub_deps, all_deps};
    const bool report_missing_direct_deps = true;
    const bool report_unused_deps = true;
    const bool optimize_impl_deps = true;

    const auto result = evaluateIncludes(pub_includes, priv_includes, system_under_inspection,
                                         report_missing_direct_deps, report_unused_deps, optimize_impl_deps);

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
    const auto pub_b = makeDep("//pub/dep:b");
    const auto priv_b = makeDep("//priv/dep:b");
    const SystemUnderInspection::HeadersToDepsMap pub_deps{
        {"path/hdr_pub_a.h", {makeDep("//pub/dep:a")}},
        // Even if multiple headers are unused, we report the dependency only once
        {"path/hdr_pub_b_1.h", {pub_b}},
        {"path/hdr_pub_b_2.h", {pub_b}}};
    const auto all_deps =
        makeAllDeps(pub_deps, {{"path/hdr_priv_a.h", {makeDep("//priv/dep:a")}},
                               // Even if multiple headers are unused, we report the dependency only once
                               {"path/hdr_priv_b_1.h", {priv_b}},
                               {"path/hdr_priv_b_2.h", {priv_b}}});

    SystemUnderInspection system_under_inspection{CcTargetUnderInspection{"//:foo", {}}, pub_deps, all_deps};
    const bool report_missing_direct_deps = true;
    const bool report_unused_deps = true;
    const bool optimize_impl_deps = false;

    const auto result = evaluateIncludes(pub_includes, priv_includes, system_under_inspection,
                                         report_missing_direct_deps, report_unused_deps, optimize_impl_deps);

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
    const auto pub_a = makeDep("//pub/dep:a");
    const SystemUnderInspection::HeadersToDepsMap pub_deps{{"path/hdr_a_1.h", {pub_a}}, {"path/hdr_a_2.h", {pub_a}}};
    const auto priv_b = makeDep("//priv/dep:b");
    const auto all_deps = makeAllDeps(pub_deps, {{"path/hdr_b_1.h", {priv_b}}, {"path/hdr_b_2.h", {priv_b}}});

    SystemUnderInspection system_under_inspection{CcTargetUnderInspection{"//:foo", {}}, pub_deps, all_deps};
    const bool report_missing_direct_deps = true;
    const bool report_unused_deps = true;
    const bool optimize_impl_deps = false;

    const auto result = evaluateIncludes(pub_includes, priv_includes, system_under_inspection,
                                         report_missing_direct_deps, report_unused_deps, optimize_impl_deps);

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
        IncludeStatement{"priv_file_using_b.cpp", "<hdr_b.h>", "path/hdr_b.h"}};
    const SystemUnderInspection::HeadersToDepsMap pub_deps{
        {"path/hdr_a.h", {makeDep("//pub/dep:a_1"), makeDep("//pub/dep:a_2")}}};
    const auto all_deps =
        makeAllDeps(pub_deps, {{"path/hdr_b.h", {makeDep("//priv/dep:b_1"), makeDep("//priv/dep:b_2")}}});
    SystemUnderInspection system_under_inspection{CcTargetUnderInspection{"//:foo", {}}, pub_deps, all_deps};
    const bool report_missing_direct_deps = true;
    const bool report_unused_deps = true;
    const bool optimize_impl_deps = false;

    const auto result = evaluateIncludes(pub_includes, priv_includes, system_under_inspection,
                                         report_missing_direct_deps, report_unused_deps, optimize_impl_deps);

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
        IncludeStatement{"priv_file_using_b.cpp", "<hdr_b_1.h>", "path/hdr_b_1.h"},
        IncludeStatement{"priv_file_using_b.cpp", "<hdr_b_2.h>", "path/hdr_b_2.h"}};
    const auto pub_b = makeDep("//pub/dep:b");
    const SystemUnderInspection::HeadersToDepsMap pub_deps{
        {"path/hdr_a.h", {makeDep("//pub/dep:a")}},
        // Even if multiple headers are unused only privately, we report the dependency only once
        {"path/hdr_b_1.h", {pub_b}},
        {"path/hdr_b_2.h", {pub_b}}};
    const auto all_deps = makeAllDeps(pub_deps, {});
    SystemUnderInspection system_under_inspection{CcTargetUnderInspection{"//:foo", {}}, pub_deps, all_deps};
    const bool report_missing_direct_deps = true;
    const bool report_unused_deps = true;
    const bool optimize_impl_deps = true;

    const auto result = evaluateIncludes(pub_includes, priv_includes, system_under_inspection,
                                         report_missing_direct_deps, report_unused_deps, optimize_impl_deps);

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

TEST(EvaluateIncludes, AllowMissingDirectDependencies) {
    const std::vector<IncludeStatement> pub_includes{
        IncludeStatement{"pub_file_using_a.h", "<pub_hdr_a.h>", "path/pub_hdr_a.h"}};
    const std::vector<IncludeStatement> priv_includes{
        IncludeStatement{"priv_file_using_b.cpp", "<priv_hdr_b.h>", "path/priv_hdr_b.h"}};
    const SystemUnderInspection::HeadersToDepsMap pub_deps{};
    const auto all_deps = makeAllDeps(pub_deps, {});

    SystemUnderInspection system_under_inspection{CcTargetUnderInspection{"//:foo", {}}, pub_deps, all_deps};
    const bool report_missing_direct_deps = false;
    const bool report_unused_deps = true;
    const bool optimize_impl_deps = false;

    const auto result = evaluateIncludes(pub_includes, priv_includes, system_under_inspection,
                                         report_missing_direct_deps, report_unused_deps, optimize_impl_deps);

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

TEST(EvaluateIncludes, AllowUnusedUnusedDependencies) {
    const std::vector<IncludeStatement> pub_includes{};
    const std::vector<IncludeStatement> priv_includes{};
    const SystemUnderInspection::HeadersToDepsMap pub_deps{{"path/hdr_pub_a.h", {makeDep("//pub/dep:a")}}};
    const auto all_deps = makeAllDeps(pub_deps, {{"path/hdr_priv_a.h", {makeDep("//priv/dep:a")}}});

    SystemUnderInspection system_under_inspection{CcTargetUnderInspection{"//:foo", {}}, pub_deps, all_deps};
    const bool report_missing_direct_deps = true;
    const bool report_unused_deps = false;
    const bool optimize_impl_deps = false;

    const auto result = evaluateIncludes(pub_includes, priv_includes, system_under_inspection,
                                         report_missing_direct_deps, report_unused_deps, optimize_impl_deps);

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

} // namespace
} // namespace dwyu
