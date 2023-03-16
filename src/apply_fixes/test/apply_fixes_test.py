import unittest
from subprocess import CompletedProcess
from unittest.mock import patch

from src.apply_fixes.apply_fixes import (
    Dependency,
    get_dependencies,
    get_file_name,
    search_missing_deps,
    target_to_file,
)


class TestApplyFixesHelper(unittest.TestCase):
    def test_get_file_name(self):
        self.assertEqual(get_file_name("foo"), "foo")
        self.assertEqual(get_file_name("foo.txt"), "foo.txt")
        self.assertEqual(get_file_name("riff/raff/foo.txt"), "foo.txt")

    def test_target_to_file(self):
        self.assertEqual(target_to_file(":foo"), "foo")
        self.assertEqual(target_to_file("@foo//bar:riff/raff.txt"), "raff.txt")


class TestGetDependencies(unittest.TestCase):
    @patch("src.apply_fixes.apply_fixes.execute_and_capture")
    def test_parse_query_output(self, execute_query_mock):
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
        deps = get_dependencies(workspace=None, target="")

        self.assertEqual(len(deps), 2)
        self.assertEqual(deps[0].target, "//foo:bar")
        self.assertEqual(deps[0].hdrs, ["riff.h", "raff.h"])
        self.assertEqual(deps[1].target, "//:foobar")
        self.assertEqual(deps[1].hdrs, ["foobar.h"])


class TestSearchDeps(unittest.TestCase):
    def test_noop_for_empty_input(self):
        self.assertEqual(search_missing_deps(workspace=None, target="", includes_without_direct_dep=[]), [])

    @patch("src.apply_fixes.apply_fixes.get_dependencies")
    def test_find_dependency(self, get_deps_mock):
        get_deps_mock.return_value = [
            Dependency(target="//unrelated:lib", hdrs=["some_include.h"]),
            Dependency(target="//expected:target", hdrs=["include_a.h", "include_b.h"]),
        ]
        deps = search_missing_deps(
            workspace=None,
            target="foo",
            includes_without_direct_dep={"some_file.cc": ["some/path/include_b.h"]},
        )

        self.assertEqual(deps, ["//expected:target"])

    @patch("src.apply_fixes.apply_fixes.get_dependencies")
    def test_fail_on_unresolved_dependency(self, get_deps_mock):
        get_deps_mock.return_value = [Dependency(target="//unrelated:lib", hdrs=["some_include.h"])]
        with self.assertLogs() as cm:
            deps = search_missing_deps(
                workspace=None,
                target="foo",
                includes_without_direct_dep={"some_file.cc": ["some/path/include_b.h"]},
            )
            self.assertTrue(
                any(
                    "WARNING:root:Could not find a proper dependency for invalid include 'some/path/include_b.h'" in out
                    for out in cm.output
                )
            )
            self.assertEqual(
                cm.output,
                [
                    "WARNING:root:Could not find a proper dependency for invalid include 'some/path/include_b.h' of target 'foo'.\n"
                    + "Is the header file maybe wrongly part of the 'srcs' attribute instead of 'hdrs' in the library which should provide the header?"
                ],
            )
            self.assertEqual(deps, [])

    @patch("src.apply_fixes.apply_fixes.get_dependencies")
    def test_fail_on_ambiguous_dependency_resolution(self, get_deps_mock):
        get_deps_mock.return_value = [
            Dependency(target="//:lib_a", hdrs=["foo.h"]),
            Dependency(target="//:lib_b", hdrs=["foo.h"]),
        ]
        with self.assertLogs() as cm:
            deps = search_missing_deps(
                workspace=None,
                target="foo",
                includes_without_direct_dep={"some_file.cc": ["some/path/foo.h"]},
            )
            self.assertEqual(
                cm.output,
                [
                    "WARNING:root:Found multiple targets which potentially can provide include 'some/path/foo.h' of target 'foo'.\n"
                    + "Please fix this manually. Candidates which have been discovered:",
                    "WARNING:root:- //:lib_a\n- //:lib_b",
                ],
            )
            self.assertEqual(deps, [])


if __name__ == "__main__":
    unittest.main()
