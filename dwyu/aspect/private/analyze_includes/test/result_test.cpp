#include "dwyu/aspect/private/analyze_includes/include_statement.h"
#include "dwyu/aspect/private/analyze_includes/result.h"

#include <gmock/gmock.h>
#include <gtest/gtest.h>
#include <nlohmann/json.hpp>

#include <set>
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

TEST(Result, IsOkByDefault) {
    const Result unit{"//:foo", true};
    EXPECT_TRUE(unit.isOk());
}

TEST(Result, IsNotOkGivenPublicIncludesWithoutDirectDep) {
    Result unit{"//:foo", true};
    unit.setPublicIncludesWithoutDirectDep({IncludeStatement{"some_file.cpp", "<include_without_direct_dep>", ""}});
    EXPECT_FALSE(unit.isOk());
}

TEST(Result, IsNotOkGivenPrivateIncludesWithoutDirectDep) {
    Result unit{"//:foo", true};
    unit.setPrivateIncludesWithoutDirectDep({IncludeStatement{"some_file.cpp", "<include_without_direct_dep>", ""}});
    EXPECT_FALSE(unit.isOk());
}

TEST(Result, IsNotOkGivenUnusedDeps) {
    Result unit{"//:foo", true};
    unit.setUnusedDeps({"unused_dep"});
    EXPECT_FALSE(unit.isOk());
}

TEST(Result, IsNotOkGivenUnusedImplDeps) {
    Result unit{"//:foo", true};
    unit.setUnusedImplDeps({"unused_impl_dep"});
    EXPECT_FALSE(unit.isOk());
}

TEST(Result, IsNotOkGivenPublicDepWhichShouldBePrivate) {
    Result unit{"//:foo", true};
    unit.setDepsWhichShouldBePrivate({"public_dep_which_should_be_private"});
    EXPECT_FALSE(unit.isOk());
}

TEST(Result, ToStringForSuccess) {
    const Result unit{"//:foo", true};
    const std::string expected_output =
        "================================================================================\n"
        "DWYU analyzing: //:foo\n"
        "\n"
        "Result: SUCCESS\n"
        "================================================================================\n";
    EXPECT_EQ(unit.toString("path/dwyu_report.json"), expected_output);
}

TEST(Result, ToStringForFailure) {
    Result unit{"//:bar", true};

    unit.setPublicIncludesWithoutDirectDep(
        {IncludeStatement{"pub_file_a.h", "<include_foo>", ""}, IncludeStatement{"pub_file_b.h", "<include_bar>", ""}});
    unit.setPrivateIncludesWithoutDirectDep({IncludeStatement{"priv_file_a.cpp", "\"include_fizz\"", ""},
                                             IncludeStatement{"priv_file_b.cpp", "\"include_buzz\"", ""}});
    unit.setUnusedDeps({"unused_dep", "another_unused_dep"});
    unit.setUnusedImplDeps({"unused_impl_dep", "another_unused_impl_dep"});
    unit.setDepsWhichShouldBePrivate(
        {"public_dep_which_should_be_private", "another_public_dep_which_should_be_private"});

    const std::string expected_output =
        "================================================================================\n"
        "DWYU analyzing: //:bar\n"
        "\n"
        "Result: FAILURE\n"
        "\n"
        "Includes which are not available from the direct dependencies:\n"
        "  In file 'pub_file_a.h' include: <include_foo>\n"
        "  In file 'pub_file_b.h' include: <include_bar>\n"
        "  In file 'priv_file_a.cpp' include: \"include_fizz\"\n"
        "  In file 'priv_file_b.cpp' include: \"include_buzz\"\n"
        "\n"
        "Unused dependencies in 'deps' (none of their headers are included):\n"
        "  another_unused_dep\n"
        "  unused_dep\n"
        "\n"
        "Unused dependencies in 'implementation_deps' (none of their headers are included):\n"
        "  another_unused_impl_dep\n"
        "  unused_impl_dep\n"
        "\n"
        "'deps' which should be moved to 'implementation_deps' (their headers are included only in private code):\n"
        "  another_public_dep_which_should_be_private\n"
        "  public_dep_which_should_be_private\n"
        "\n"
        "DWYU Report: path/dwyu_report.json\n"
        "================================================================================\n";
    EXPECT_EQ(unit.toString("path/dwyu_report.json"), expected_output);
}

TEST(Result, dumpToJsonForSuccess) {
    const Result unit{"//:foo", true};

    const auto data = unit.toJson();

    EXPECT_EQ(data["analyzed_target"], "//:foo");
    EXPECT_TRUE(data["public_includes_without_dep"].empty());
    EXPECT_TRUE(data["private_includes_without_dep"].empty());
    EXPECT_TRUE(data["unused_deps"].empty());
    EXPECT_TRUE(data["unused_implementation_deps"].empty());
    EXPECT_TRUE(data["deps_which_should_be_private"].empty());
    EXPECT_TRUE(data["use_implementation_deps"].get<bool>());
}

TEST(Result, dumpToJsonForFailure) {
    const std::set<std::string> unused_deps{"unused_dep", "another_unused_dep"};
    const std::set<std::string> unused_impl_deps{"unused_impl_dep", "another_unused_impl_dep"};
    const std::set<std::string> public_deps_which_should_be_private{"public_dep_which_should_be_private",
                                                                    "another_public_dep_which_should_be_private"};

    Result unit{"//:bar", false};
    unit.setUnusedDeps(unused_deps);
    unit.setUnusedImplDeps(unused_impl_deps);
    unit.setDepsWhichShouldBePrivate(public_deps_which_should_be_private);
    unit.setPublicIncludesWithoutDirectDep({IncludeStatement{"pub_file_a.h", "<include_foo_1>", ""},
                                            IncludeStatement{"pub_file_a.h", "<include_foo_2>", ""},
                                            IncludeStatement{"pub_file_b.h", "<include_bar>", ""}});
    unit.setPrivateIncludesWithoutDirectDep({IncludeStatement{"priv_file_a.cpp", "\"include_fizz\"", ""},
                                             IncludeStatement{"priv_file_b.cpp", "\"include_buzz_1\"", ""},
                                             IncludeStatement{"priv_file_b.cpp", "\"include_buzz_2\"", ""}});

    const auto data = unit.toJson();

    EXPECT_EQ(data["analyzed_target"], "//:bar");
    EXPECT_EQ(data["unused_deps"], unused_deps);
    EXPECT_EQ(data["unused_implementation_deps"], unused_impl_deps);
    EXPECT_EQ(data["deps_which_should_be_private"], public_deps_which_should_be_private);
    EXPECT_FALSE(data["use_implementation_deps"].get<bool>());

    ASSERT_THAT(getMapKeys(data["public_includes_without_dep"]),
                testing::UnorderedElementsAre("pub_file_a.h", "pub_file_b.h"));
    EXPECT_THAT(data["public_includes_without_dep"]["pub_file_a.h"].get<std::vector<std::string>>(),
                testing::UnorderedElementsAre("include_foo_1", "include_foo_2"));
    EXPECT_THAT(data["public_includes_without_dep"]["pub_file_b.h"].get<std::vector<std::string>>(),
                testing::UnorderedElementsAre("include_bar"));

    ASSERT_THAT(getMapKeys(data["private_includes_without_dep"]),
                testing::UnorderedElementsAre("priv_file_a.cpp", "priv_file_b.cpp"));
    EXPECT_THAT(data["private_includes_without_dep"]["priv_file_a.cpp"].get<std::vector<std::string>>(),
                testing::UnorderedElementsAre("include_fizz"));
    EXPECT_THAT(data["private_includes_without_dep"]["priv_file_b.cpp"].get<std::vector<std::string>>(),
                testing::UnorderedElementsAre("include_buzz_1", "include_buzz_2"));
}

} // namespace
} // namespace dwyu
