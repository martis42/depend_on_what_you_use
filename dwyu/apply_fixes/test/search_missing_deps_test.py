import unittest
from subprocess import CompletedProcess
from unittest.mock import MagicMock, patch

from dwyu.apply_fixes.search_missing_deps import (
    Dependency,
    get_dependencies,
    get_file_name,
    search_missing_deps,
    target_to_path,
)


class TestApplyFixesHelper(unittest.TestCase):
    def test_get_file_name(self) -> None:
        self.assertEqual(get_file_name("foo"), "foo")
        self.assertEqual(get_file_name("foo.txt"), "foo.txt")
        self.assertEqual(get_file_name("riff/raff/foo.txt"), "foo.txt")

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
        self.assertEqual(deps[0].include_paths, ["foo/riff.h", "foo/raff.h"])
        self.assertEqual(deps[1].target, "//:foobar")
        self.assertEqual(deps[1].include_paths, ["foobar.h"])

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
        self.assertEqual(deps[0].include_paths, ["foo/riff.h", "foo/raff.h"])
        self.assertEqual(deps[1].target, "//:foobar")
        self.assertEqual(deps[1].include_paths, ["foobar.h"])


class TestSearchDeps(unittest.TestCase):
    def test_noop_for_empty_input(self) -> None:
        self.assertEqual(search_missing_deps(bazel_query=MagicMock(), target="", includes_without_direct_dep={}), [])

    @patch("dwyu.apply_fixes.search_missing_deps.get_dependencies")
    @patch("dwyu.apply_fixes.search_missing_deps.is_visible", return_value=True)
    def test_find_dependency(self, _: MagicMock, get_deps_mock: MagicMock) -> None:
        get_deps_mock.return_value = [
            Dependency(target="//unrelated:lib", include_paths=["some_hdr.h"]),
            Dependency(target="//expected:target", include_paths=["other/path/hdr_a.h", "some/path/hdr_b.h"]),
        ]
        deps = search_missing_deps(
            bazel_query=MagicMock(),
            target="foo",
            includes_without_direct_dep={"some_file.cc": ["some/path/hdr_b.h"]},
        )

        self.assertEqual(deps, ["//expected:target"])

    @patch("dwyu.apply_fixes.search_missing_deps.get_dependencies")
    @patch("dwyu.apply_fixes.search_missing_deps.is_visible", return_value=False)
    def test_fail_for_invisible_dependency(self, _: MagicMock, get_deps_mock: MagicMock) -> None:
        get_deps_mock.return_value = [
            Dependency(target="//expected:target", include_paths=["some/path/hdr.h"]),
        ]
        with self.assertLogs() as cm:
            deps = search_missing_deps(
                bazel_query=MagicMock(),
                target="foo",
                includes_without_direct_dep={"some_file.cc": ["some/path/hdr.h"]},
            )
            self.assertEqual(len(cm.output), 1)
            self.assertTrue(
                "Could not find a proper dependency for invalid include path 'some/path/hdr.h' of target 'foo'."
                in cm.output[0]
            )
            self.assertEqual(deps, [])

    @patch("dwyu.apply_fixes.search_missing_deps.get_dependencies")
    @patch("dwyu.apply_fixes.search_missing_deps.is_visible", return_value=True)
    def test_fail_on_ambiguous_dependency_resolution_for_full_include_path(
        self, _: MagicMock, get_deps_mock: MagicMock
    ) -> None:
        get_deps_mock.return_value = [
            Dependency(target="//:lib_a", include_paths=["some/path/foo.h"]),
            Dependency(target="//:lib_b", include_paths=["some/path/foo.h"]),
        ]
        with self.assertLogs() as cm:
            deps = search_missing_deps(
                bazel_query=MagicMock(),
                target="foo",
                includes_without_direct_dep={"some_file.cc": ["some/path/foo.h"]},
            )
            self.assertEqual(len(cm.output), 1)
            self.assertTrue(
                "Found multiple targets providing invalid include path 'some/path/foo.h' of target 'foo'"
                in cm.output[0]
            )
            self.assertTrue("Discovered potential dependencies are: ['//:lib_a', '//:lib_b']" in cm.output[0])
            self.assertEqual(deps, [])

    @patch("dwyu.apply_fixes.search_missing_deps.get_dependencies")
    @patch("dwyu.apply_fixes.search_missing_deps.is_visible", return_value=True)
    def test_find_dependency_via_file_name_fallback(self, _: MagicMock, get_deps_mock: MagicMock) -> None:
        get_deps_mock.return_value = [
            Dependency(target="//some:lib_a", include_paths=["foo.h"]),
        ]
        deps = search_missing_deps(
            bazel_query=MagicMock(),
            target="foo",
            includes_without_direct_dep={"some_file.cc": ["some/path/foo.h"]},
        )
        self.assertEqual(deps, ["//some:lib_a"])

    @patch("dwyu.apply_fixes.search_missing_deps.get_dependencies")
    @patch("dwyu.apply_fixes.search_missing_deps.is_visible", return_value=True)
    def test_fail_on_ambiguous_dependency_resolution_for_file_name_fallback(
        self, _: MagicMock, get_deps_mock: MagicMock
    ) -> None:
        get_deps_mock.return_value = [
            Dependency(target="//:lib_a", include_paths=["foo.h"]),
            Dependency(target="//:lib_b", include_paths=["foo.h"]),
        ]
        with self.assertLogs() as cm:
            deps = search_missing_deps(
                bazel_query=MagicMock(),
                target="foo",
                includes_without_direct_dep={"some_file.cc": ["some/path/foo.h"]},
            )
            self.assertEqual(len(cm.output), 1)
            self.assertTrue(
                "Found multiple targets providing file 'foo.h' from invalid include 'some/path/foo.h' of target 'foo'"
                in cm.output[0]
            )
            self.assertTrue("Discovered potential dependencies are: ['//:lib_a', '//:lib_b']" in cm.output[0])
            self.assertEqual(deps, [])

    @patch("dwyu.apply_fixes.search_missing_deps.get_dependencies")
    def test_fail_on_unresolved_dependency(self, get_deps_mock: MagicMock) -> None:
        get_deps_mock.return_value = [Dependency(target="//unrelated:lib", include_paths=["some_hdr.h"])]
        with self.assertLogs() as cm:
            deps = search_missing_deps(
                bazel_query=MagicMock(),
                target="foo",
                includes_without_direct_dep={"some_file.cc": ["some/path/hdr.h"]},
            )
            self.assertEqual(len(cm.output), 1)
            self.assertTrue(
                "Could not find a proper dependency for invalid include path 'some/path/hdr.h' of target 'foo'"
                in cm.output[0]
            )
            self.assertEqual(deps, [])


if __name__ == "__main__":
    unittest.main()
