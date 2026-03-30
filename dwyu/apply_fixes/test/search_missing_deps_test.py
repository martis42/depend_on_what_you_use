import unittest
from subprocess import CompletedProcess
from unittest.mock import MagicMock, patch

from dwyu.apply_fixes.search_missing_deps import (
    Dependency,
    get_dependencies,
    search_missing_deps,
    target_to_path,
)


class TestApplyFixesHelper(unittest.TestCase):
    def test_target_to_path(self) -> None:
        self.assertEqual(target_to_path("//:foo"), "foo")
        self.assertEqual(target_to_path("@foo//bar:riff/raff.txt"), "bar/riff/raff.txt")


class TestGetDependencies(unittest.TestCase):
    def test_target_without_dependencies(self) -> None:
        execute_query_mock = MagicMock()
        execute_query_mock.configure_mock(
            uses_cquery=False,
            **{
                "execute.return_value": CompletedProcess(
                    args=[],
                    returncode=0,
                    stderr="",
                    stdout="",
                ),
            },
        )
        deps = get_dependencies(bazel_query=execute_query_mock, target="")

        self.assertEqual(deps, [])

    def test_parse_query_output(self) -> None:
        execute_query_mock = MagicMock()
        execute_query_mock.configure_mock(
            uses_cquery=False,
            **{
                "execute.return_value": CompletedProcess(
                    args=[],
                    returncode=0,
                    stderr="",
                    stdout="""
{"type":"RULE","rule":{"name":"//foo:bar","ruleClass":"cc_library","attribute":[{"name":"unrelated"},{"name":"hdrs","type":"LABEL_LIST","stringListValue":["//foo:riff.h", "//foo:raff.h"],"explicitlySpecified":true,"nodep":false}]}}
{"type":"RULE","rule":{"name":"//:foobar","ruleClass":"cc_library","attribute":[{"name":"unrelated"},{"name":"hdrs","type":"LABEL_LIST","stringListValue":["//:foobar.h"],"explicitlySpecified":true,"nodep":false}]}}
{"type":"RULE","rule":{"name":"//:buzz","ruleClass":"unrelated_rule"}}
{"type":"UNRELATED"}
""".strip(),
                ),
            },
        )
        deps = get_dependencies(bazel_query=execute_query_mock, target="")

        self.assertEqual(len(deps), 2)
        self.assertEqual(deps[0].target, "//foo:bar")
        self.assertEqual(deps[0].headers, ["foo/riff.h", "foo/raff.h"])
        self.assertEqual(deps[1].target, "//:foobar")
        self.assertEqual(deps[1].headers, ["foobar.h"])

    def test_parse_cquery_output(self) -> None:
        execute_query_mock = MagicMock()
        execute_query_mock.configure_mock(
            uses_cquery=True,
            **{
                "execute.return_value": CompletedProcess(
                    args=[],
                    returncode=0,
                    stderr="",
                    stdout="""
{
  "results": [
    {"target": {"type":"RULE","rule":{"name":"//foo:bar","ruleClass":"cc_library","attribute":[{"name":"unrelated"},{"name":"hdrs","type":"LABEL_LIST","stringListValue":["//foo:riff.h", "//foo:raff.h"],"explicitlySpecified":true,"nodep":false}]}}},
    {"target": {"type":"RULE","rule":{"name":"//:foobar","ruleClass":"cc_library","attribute":[{"name":"unrelated"},{"name":"hdrs","type":"LABEL_LIST","stringListValue":["//:foobar.h"],"explicitlySpecified":true,"nodep":false}]}}},
    {"target": {"type": "RULE", "rule": {"name":"//:buzz","ruleClass":"unrelated_rule"}}},
    {"target": {"type": "UNRELATED"}}
  ]
}
""".strip(),
                ),
            },
        )
        deps = get_dependencies(bazel_query=execute_query_mock, target="")

        self.assertEqual(len(deps), 2)
        self.assertEqual(deps[0].target, "//foo:bar")
        self.assertEqual(deps[0].headers, ["foo/riff.h", "foo/raff.h"])
        self.assertEqual(deps[1].target, "//:foobar")
        self.assertEqual(deps[1].headers, ["foobar.h"])

    def test_parse_output_for_target_using_virtual_headers(self) -> None:
        def make_query_result(target: str, hdrs: str, added_prefix: str = "", stripped_prefix: str = "") -> str:
            name = target.rsplit(":", maxsplit=1)[1]

            rule_part = '{"type":"RULE","rule":{"name":"' + target + '","ruleClass":"cc_library","attribute":['
            attr_name = '{"name":"name","type":"STRING","stringValue":"' + name + '","explicitlySpecified":true}'
            attr_hdrs = ',{"name":"hdrs","type":"LABEL_LIST","stringListValue":' + hdrs + ',"explicitlySpecified":true}'
            attr_add = (
                ',{"name":"include_prefix","type":"STRING","stringValue":"'
                + added_prefix
                + '","explicitlySpecified":true}'
                if added_prefix
                else ""
            )
            attr_strip = (
                ',{"name":"strip_include_prefix","type":"STRING","stringValue":"'
                + stripped_prefix
                + '","explicitlySpecified":true}'
                if stripped_prefix
                else ""
            )

            return rule_part + attr_name + attr_hdrs + attr_add + attr_strip + "]}}"

        execute_query_mock = MagicMock()
        strip_target = make_query_result(
            target="//:stripped_prefix", hdrs='["//:foo/bar/stripped.h"]', stripped_prefix="foo"
        )
        adding_target = make_query_result(target="//foo:adding_prefix", hdrs='["//foo:adding.h"]', added_prefix="bar")
        adding_and_strip_target = make_query_result(
            target="//foo:adding_and_stripping_prefix",
            hdrs='["//foo:sub/adding_and_stripping.h"]',
            added_prefix="bar",
            stripped_prefix="sub",
        )
        execute_query_mock.configure_mock(
            uses_cquery=False,
            **{
                "execute.return_value": CompletedProcess(
                    args=[],
                    returncode=0,
                    stderr="",
                    stdout=f"{strip_target}\n{adding_target}\n{adding_and_strip_target}",
                ),
            },
        )
        deps = get_dependencies(bazel_query=execute_query_mock, target="")

        self.assertEqual(len(deps), 3)
        self.assertEqual(deps[0].target, "//:stripped_prefix")
        self.assertEqual(
            deps[0].headers,
            [
                "foo/bar/stripped.h",
                "_virtual_includes/stripped_prefix/bar/stripped.h",
                "_virtual_includes/fc3740cb/bar/stripped.h",
            ],
        )
        self.assertEqual(deps[1].target, "//foo:adding_prefix")
        self.assertEqual(
            deps[1].headers,
            [
                "foo/adding.h",
                "foo/_virtual_includes/adding_prefix/bar/adding.h",
                "_virtual_includes/44d7767/bar/adding.h",
            ],
        )
        self.assertEqual(deps[2].target, "//foo:adding_and_stripping_prefix")
        self.assertEqual(
            deps[2].headers,
            [
                "foo/sub/adding_and_stripping.h",
                "foo/_virtual_includes/adding_and_stripping_prefix/bar/adding_and_stripping.h",
                "_virtual_includes/c98ec564/bar/adding_and_stripping.h",
            ],
        )


class TestSearchDeps(unittest.TestCase):
    def test_noop_for_empty_input(self) -> None:
        self.assertEqual(search_missing_deps(bazel_query=MagicMock(), target="", headers_without_direct_dep={}), [])

    @patch("dwyu.apply_fixes.search_missing_deps.get_dependencies")
    @patch("dwyu.apply_fixes.search_missing_deps.is_visible", return_value=True)
    def test_find_dependency(self, _: MagicMock, get_deps_mock: MagicMock) -> None:
        get_deps_mock.return_value = [
            Dependency(target="//unrelated:lib", headers=["some_hdr.h"]),
            Dependency(target="//expected:target", headers=["other/path/hdr_a.h", "some/path/hdr_b.h"]),
        ]
        deps = search_missing_deps(
            bazel_query=MagicMock(), target="foo", headers_without_direct_dep={"some_file.cc": ["some/path/hdr_b.h"]}
        )

        self.assertEqual(deps, ["//expected:target"])

    @patch("dwyu.apply_fixes.search_missing_deps.get_dependencies")
    @patch("dwyu.apply_fixes.search_missing_deps.is_visible", return_value=True)
    def test_find_dependency_for_generated_code(self, _: MagicMock, get_deps_mock: MagicMock) -> None:
        get_deps_mock.return_value = [
            Dependency(target="//expected:target", headers=["other/path/hdr_a.h", "some/path/hdr_b.h"]),
        ]
        deps = search_missing_deps(
            bazel_query=MagicMock(),
            target="foo",
            headers_without_direct_dep={"some_file.cc": ["bazel-out/k8-fastbuild/bin/some/path/hdr_b.h"]},
        )

        self.assertEqual(deps, ["//expected:target"])

    @patch("dwyu.apply_fixes.search_missing_deps.get_dependencies")
    @patch("dwyu.apply_fixes.search_missing_deps.is_visible", return_value=True)
    def test_find_dependency_for_external_code(self, _: MagicMock, get_deps_mock: MagicMock) -> None:
        get_deps_mock.return_value = [
            Dependency(target="@some_repo//expected:target", headers=["other/path/hdr_a.h", "some/path/hdr_b.h"]),
        ]
        deps = search_missing_deps(
            bazel_query=MagicMock(),
            target="foo",
            headers_without_direct_dep={"some_file.cc": ["external/some_repo/some/path/hdr_b.h"]},
        )

        self.assertEqual(deps, ["@some_repo//expected:target"])

    @patch("dwyu.apply_fixes.search_missing_deps.get_dependencies")
    @patch("dwyu.apply_fixes.search_missing_deps.is_visible", return_value=False)
    def test_fail_for_invisible_dependency(self, _: MagicMock, get_deps_mock: MagicMock) -> None:
        get_deps_mock.return_value = [
            Dependency(target="//expected:target", headers=["some/path/hdr.h"]),
        ]
        with self.assertLogs() as cm:
            deps = search_missing_deps(
                bazel_query=MagicMock(), target="foo", headers_without_direct_dep={"some_file.cc": ["some/path/hdr.h"]}
            )
            self.assertEqual(len(cm.output), 1)
            self.assertTrue(
                "Could not find a dependency providing providing the header file 'some/path/hdr.h' for target 'foo'."
                in cm.output[0]
            )
            self.assertEqual(deps, [])

    @patch("dwyu.apply_fixes.search_missing_deps.get_dependencies")
    @patch("dwyu.apply_fixes.search_missing_deps.is_visible", return_value=True)
    def test_fail_on_ambiguous_dependency_resolution_for_header_file(
        self, _: MagicMock, get_deps_mock: MagicMock
    ) -> None:
        get_deps_mock.return_value = [
            Dependency(target="//:lib_a", headers=["some/path/foo.h"]),
            Dependency(target="//:lib_b", headers=["some/path/foo.h"]),
        ]
        with self.assertLogs() as cm:
            deps = search_missing_deps(
                bazel_query=MagicMock(), target="foo", headers_without_direct_dep={"some_file.cc": ["some/path/foo.h"]}
            )
            self.assertEqual(len(cm.output), 1)
            self.assertTrue(
                "Found multiple targets providing the header file 'some/path/foo.h' required by target 'foo'"
                in cm.output[0]
            )
            self.assertTrue("Discovered potential dependencies are: ['//:lib_a', '//:lib_b']" in cm.output[0])
            self.assertEqual(deps, [])

    @patch("dwyu.apply_fixes.search_missing_deps.get_dependencies")
    def test_fail_on_unresolved_dependency(self, get_deps_mock: MagicMock) -> None:
        get_deps_mock.return_value = [Dependency(target="//unrelated:lib", headers=["some_hdr.h"])]
        with self.assertLogs() as cm:
            deps = search_missing_deps(
                bazel_query=MagicMock(), target="foo", headers_without_direct_dep={"some_file.cc": ["some/path/hdr.h"]}
            )
            self.assertEqual(len(cm.output), 1)
            self.assertTrue(
                "Could not find a dependency providing providing the header file 'some/path/hdr.h' for target 'foo'."
                in cm.output[0]
            )
            self.assertEqual(deps, [])


if __name__ == "__main__":
    unittest.main()
