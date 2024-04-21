import unittest
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import MagicMock, patch

from src.apply_fixes.apply_fixes import (
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
    @patch("src.apply_fixes.apply_fixes.execute_and_capture")
    def test_parse_query_output(self, execute_query_mock: MagicMock) -> None:
        execute_query_mock.return_value = CompletedProcess(
            args=[],
            returncode=0,
            stderr="",
            stdout="""
<?xml version="1.1" encoding="UTF-8" standalone="no"?>
<query version="2">
    <rule class="cc_library" location="/foo/BUILD:13:37" name="//foo:bar">
        <string name="name" value="bar"/>
        <list name="hdrs">
            <label value="//foo:riff.h"/>
            <label value="//foo:raff.h"/>
        </list>
        <rule-input name="//foo:riff.h"/>
        <rule-input name="//foo:raff.h"/>
    </rule>
    <rule class="cc_library" location="/BUILD:1:11" name="//:foobar">
        <string name="name" value="foobar"/>
        <list name="hdrs">
            <label value="//:foobar.h"/>
        </list>
        <rule-input name="//:foobar.h"/>
    </rule>
</query>
""".strip(),
        )
        deps = get_dependencies(workspace=Path(), target="")

        self.assertEqual(len(deps), 2)
        self.assertEqual(deps[0].target, "//foo:bar")
        self.assertEqual(deps[0].include_paths, ["foo/riff.h", "foo/raff.h"])
        self.assertEqual(deps[1].target, "//:foobar")
        self.assertEqual(deps[1].include_paths, ["foobar.h"])


class TestSearchDeps(unittest.TestCase):
    def test_noop_for_empty_input(self) -> None:
        self.assertEqual(search_missing_deps(workspace=Path(), target="", includes_without_direct_dep={}), [])

    @patch("src.apply_fixes.apply_fixes.get_dependencies")
    def test_find_dependency(self, get_deps_mock: MagicMock) -> None:
        get_deps_mock.return_value = [
            Dependency(target="//unrelated:lib", include_paths=["some_include.h"]),
            Dependency(target="//expected:target", include_paths=["other/path/include_a.h", "some/path/include_b.h"]),
        ]
        deps = search_missing_deps(
            workspace=Path(),
            target="foo",
            includes_without_direct_dep={"some_file.cc": ["some/path/include_b.h"]},
        )

        self.assertEqual(deps, ["//expected:target"])

    @patch("src.apply_fixes.apply_fixes.get_dependencies")
    def test_fail_on_ambiguous_dependency_resolution_for_full_include_path(self, get_deps_mock: MagicMock) -> None:
        get_deps_mock.return_value = [
            Dependency(target="//:lib_a", include_paths=["some/path/foo.h"]),
            Dependency(target="//:lib_b", include_paths=["some/path/foo.h"]),
        ]
        with self.assertLogs() as cm:
            deps = search_missing_deps(
                workspace=Path(),
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

    @patch("src.apply_fixes.apply_fixes.get_dependencies")
    def test_find_dependency_via_file_name_fallback(self, get_deps_mock: MagicMock) -> None:
        get_deps_mock.return_value = [
            Dependency(target="//some:lib_a", include_paths=["foo.h"]),
        ]
        deps = search_missing_deps(
            workspace=Path(),
            target="foo",
            includes_without_direct_dep={"some_file.cc": ["some/path/foo.h"]},
        )
        self.assertEqual(deps, ["//some:lib_a"])

    @patch("src.apply_fixes.apply_fixes.get_dependencies")
    def test_fail_on_ambiguous_dependency_resolution_for_file_name_fallback(self, get_deps_mock: MagicMock) -> None:
        get_deps_mock.return_value = [
            Dependency(target="//:lib_a", include_paths=["foo.h"]),
            Dependency(target="//:lib_b", include_paths=["foo.h"]),
        ]
        with self.assertLogs() as cm:
            deps = search_missing_deps(
                workspace=Path(),
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

    @patch("src.apply_fixes.apply_fixes.get_dependencies")
    def test_fail_on_unresolved_dependency(self, get_deps_mock: MagicMock) -> None:
        get_deps_mock.return_value = [Dependency(target="//unrelated:lib", include_paths=["some_include.h"])]
        with self.assertLogs() as cm:
            deps = search_missing_deps(
                workspace=Path(),
                target="foo",
                includes_without_direct_dep={"some_file.cc": ["some/path/include_b.h"]},
            )
            self.assertEqual(len(cm.output), 1)
            self.assertTrue(
                "Could not find a proper dependency for invalid include path 'some/path/include_b.h' of target 'foo'"
                in cm.output[0]
            )
            self.assertEqual(deps, [])


if __name__ == "__main__":
    unittest.main()
