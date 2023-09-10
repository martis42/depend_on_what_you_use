import unittest
from pathlib import Path

from src.analyze_includes.evaluate_includes import (
    does_include_match_available_files,
    evaluate_includes,
)
from src.analyze_includes.parse_source import Include
from src.analyze_includes.system_under_inspection import CcTarget, SystemUnderInspection


class TestIncludeTofileMatching(unittest.TestCase):
    def test_match_with_standard_include_path(self):
        self.assertTrue(
            does_include_match_available_files(include_statement="foo.h", include_paths=[""], header_files=["foo.h"])
        )
        self.assertTrue(
            does_include_match_available_files(
                include_statement="some/path/foo.h", include_paths=[""], header_files=["some/path/foo.h"]
            )
        )
        self.assertTrue(
            does_include_match_available_files(
                include_statement="foo.h",
                include_paths=["", "unrelated/path"],
                header_files=["foo.h", "unrelated/file.h"],
            )
        )

    def test_no_match_with_standard_include_path(self):
        self.assertFalse(
            does_include_match_available_files(include_statement="foo.h", include_paths=[""], header_files=[])
        )
        self.assertFalse(
            does_include_match_available_files(include_statement="foo.h", include_paths=[""], header_files=["bar.h"])
        )
        self.assertFalse(
            does_include_match_available_files(
                include_statement="foo.h",
                include_paths=["", "unrelated/path"],
                header_files=["bar.h", "unrelated/file.h", "not/matching/foo.h"],
            )
        )

    def test_match_based_on_non_standard_include_path(self):
        self.assertTrue(
            does_include_match_available_files(
                include_statement="foo.h", include_paths=["some/dir"], header_files=["some/dir/foo.h"]
            )
        )

    def test_no_match_based_on_non_standard_include_path(self):
        self.assertFalse(
            does_include_match_available_files(
                include_statement="foo.h", include_paths=["some/dir"], header_files=["some/dir/bar.h", "wrong/foo.h"]
            )
        )


class TestEvaluateIncludes(unittest.TestCase):
    def test_success_for_valid_dependencies(self):
        result = evaluate_includes(
            public_includes=[
                Include(file=Path("file1"), include="foo.h"),
                Include(file=Path("file2"), include="foo/bar.h"),
            ],
            private_includes=[
                Include(file=Path("file3"), include="baz.h"),
                Include(file=Path("file4"), include="self/own_header.h"),
            ],
            system_under_inspection=SystemUnderInspection(
                target_under_inspection=CcTarget(name="foo", header_files=["self/own_header.h"]),
                deps=[
                    CcTarget(name="foo_pkg", header_files=["foo.h", "foo/bar.h"]),
                    CcTarget(name="lib_without_hdrs_purely_for_linking", header_files=[]),
                ],
                implementation_deps=[CcTarget(name="baz_pkg", header_files=["baz.h"])],
                include_paths=[""],
                defines=[],
            ),
            ensure_private_deps=True,
        )

        self.assertTrue(result.is_ok())

    def test_success_for_valid_dependencies_with_virtual_include_paths(self):
        result = evaluate_includes(
            public_includes=[
                Include(file=Path("file1"), include="foo.h"),
                Include(file=Path("file2"), include="dir/bar.h"),
            ],
            private_includes=[Include(file=Path("file4"), include="path/baz.h")],
            system_under_inspection=SystemUnderInspection(
                target_under_inspection=CcTarget(name="foo", header_files=["self/own_header.h"]),
                deps=[CcTarget(name="foo_pkg", header_files=["foo.h", "some/virtual/dir/bar.h"])],
                implementation_deps=[CcTarget(name="baz_pkg", header_files=["long/nested/path/baz.h"])],
                include_paths=["", "long/nested", "some/virtual"],
                defines=[],
            ),
            ensure_private_deps=True,
        )

        self.assertTrue(result.is_ok())

    def test_success_for_valid_dependencies_with_virtual_include_paths_and_relative_include_statements(self):
        result = evaluate_includes(
            public_includes=[
                Include(file=Path("file1"), include="../../self/own_header.h"),
                Include(file=Path("file1"), include="some/virtual/../../dir/foo.h"),
            ],
            private_includes=[Include(file=Path("file2"), include="some/../../../some/virtual/dir/bar.h")],
            system_under_inspection=SystemUnderInspection(
                target_under_inspection=CcTarget(name="self", header_files=["self/own_header.h"]),
                deps=[CcTarget(name="foo_pkg", header_files=["dir/foo.h"])],
                implementation_deps=[CcTarget(name="bar_pkg", header_files=["some/virtual/dir/bar.h"])],
                include_paths=["", "some/virtual", "other/virtual"],
                defines=[],
            ),
            ensure_private_deps=True,
        )

        self.assertTrue(result.is_ok())

    def test_success_for_internal_relative_includes_with_flat_structure(self):
        result = evaluate_includes(
            public_includes=[Include(file=Path("foo.h"), include="bar.h")],
            private_includes=[],
            system_under_inspection=SystemUnderInspection(
                target_under_inspection=CcTarget(name="foo", header_files=["foo.h", "bar.h"]),
                deps=[],
                implementation_deps=[],
                include_paths=[""],
                defines=[],
            ),
            ensure_private_deps=True,
        )

        self.assertTrue(result.is_ok())

    def test_success_for_internal_relative_includes_with_nested_structure(self):
        result = evaluate_includes(
            public_includes=[
                Include(file=Path("nested/dir/foo.h"), include="bar.h"),
                Include(file=Path("nested/dir/foo.h"), include="sub/tick.h"),
                Include(file=Path("nested/dir/foo.h"), include="../../nested/dir/sub/tick.h"),
                Include(file=Path("nested/dir/sub/tick.h"), include="tock.h"),
            ],
            private_includes=[],
            system_under_inspection=SystemUnderInspection(
                target_under_inspection=CcTarget(
                    name="foo",
                    header_files=[
                        "nested/dir/foo.h",
                        "nested/dir/bar.h",
                        "nested/dir/sub/tick.h",
                        "nested/dir/sub/tock.h",
                    ],
                ),
                deps=[],
                implementation_deps=[],
                include_paths=[""],
                defines=[],
            ),
            ensure_private_deps=True,
        )

        self.assertTrue(result.is_ok())

    def test_success_for_relative_includes_to_dependency(self):
        result = evaluate_includes(
            public_includes=[
                Include(file=Path("bar/dir/bar.h"), include="sub/tick.h"),
                Include(file=Path("bar/dir/bar.h"), include="../dir/sub/tick.h"),
                Include(file=Path("bar/dir/sub/tick.h"), include="tock.h"),
            ],
            private_includes=[],
            system_under_inspection=SystemUnderInspection(
                target_under_inspection=CcTarget(name="foo", header_files=["foo.h"]),
                deps=[
                    CcTarget(
                        name="bar",
                        header_files=["bar/dir/bar.h", "bar/dir/sub/tick.h", "bar/dir/sub/tock.h"],
                    )
                ],
                implementation_deps=[],
                include_paths=[""],
                defines=[],
            ),
            ensure_private_deps=True,
        )

        self.assertTrue(result.is_ok())

    def test_invalid_includes_missing_internal_include(self):
        result = evaluate_includes(
            public_includes=[Include(file=Path("some/dir/foo.h"), include="tick.h")],
            private_includes=[Include(file=Path("some/dir/bar.h"), include="tock.h")],
            # Make sure files with the required name which are at the wrong location are ignored
            system_under_inspection=SystemUnderInspection(
                target_under_inspection=CcTarget(
                    name="foo",
                    header_files=["some/dir/foo.h", "some/dir/bar.h", "unrelated/dir/tick.h", "unrelated/dir/tock.h"],
                ),
                deps=[],
                implementation_deps=[],
                include_paths=[""],
                defines=[],
            ),
            ensure_private_deps=True,
        )

        self.assertFalse(result.is_ok())
        self.assertEqual(result.unused_deps, [])
        self.assertEqual(result.unused_implementation_deps, [])
        self.assertEqual(result.deps_which_should_be_private, [])
        self.assertEqual(result.public_includes_without_dep, [Include(file=Path("some/dir/foo.h"), include="tick.h")])
        self.assertEqual(result.private_includes_without_dep, [Include(file=Path("some/dir/bar.h"), include="tock.h")])

    def test_missing_includes_from_dependencies(self):
        result = evaluate_includes(
            public_includes=[
                Include(file=Path("public_file"), include="foo.h"),
                Include(file=Path("public_file"), include="foo/foo.h"),
                Include(file=Path("public_file"), include="foo/bar.h"),
            ],
            private_includes=[
                Include(file=Path("private_file"), include="bar.h"),
                Include(file=Path("private_file"), include="bar/foo.h"),
                Include(file=Path("private_file"), include="bar/bar.h"),
            ],
            system_under_inspection=SystemUnderInspection(
                target_under_inspection=CcTarget(name="foo", header_files=[]),
                deps=[CcTarget(name="foo", header_files=["foo.h"])],
                implementation_deps=[CcTarget(name="bar", header_files=["bar.h"])],
                include_paths=[""],
                defines=[],
            ),
            ensure_private_deps=True,
        )

        self.assertFalse(result.is_ok())
        self.assertEqual(result.unused_deps, [])
        self.assertEqual(result.unused_implementation_deps, [])
        self.assertEqual(result.deps_which_should_be_private, [])
        self.assertEqual(len(result.public_includes_without_dep), 2)
        self.assertTrue(Include(file=Path("public_file"), include="foo/foo.h") in result.public_includes_without_dep)
        self.assertTrue(Include(file=Path("public_file"), include="foo/bar.h") in result.public_includes_without_dep)
        self.assertEqual(len(result.private_includes_without_dep), 2)
        self.assertTrue(Include(file=Path("private_file"), include="bar/foo.h") in result.private_includes_without_dep)
        self.assertTrue(Include(file=Path("private_file"), include="bar/bar.h") in result.private_includes_without_dep)

    def test_unused_dependencies(self):
        result = evaluate_includes(
            public_includes=[Include(file=Path("public_file"), include="foobar.h")],
            private_includes=[Include(file=Path("private_file"), include="impl_dep.h")],
            system_under_inspection=SystemUnderInspection(
                target_under_inspection=CcTarget(name="foo", header_files=[]),
                deps=[
                    CcTarget(name="foobar", header_files=["foobar.h"]),
                    CcTarget(name="foo", header_files=["foo.h"]),
                    CcTarget(name="bar", header_files=["bar.h"]),
                ],
                implementation_deps=[
                    CcTarget(name="impl_dep", header_files=["impl_dep.h"]),
                    CcTarget(name="impl_foo", header_files=["impl_dep_foo.h"]),
                    CcTarget(name="impl_bar", header_files=["impl_dep_bar.h"]),
                ],
                include_paths=[""],
                defines=[],
            ),
            ensure_private_deps=True,
        )

        self.assertFalse(result.is_ok())
        self.assertEqual(result.public_includes_without_dep, [])
        self.assertEqual(result.private_includes_without_dep, [])
        self.assertEqual(result.deps_which_should_be_private, [])
        self.assertEqual(len(result.unused_deps), 2)
        self.assertEqual(len(result.unused_implementation_deps), 2)
        self.assertTrue("foo" in result.unused_deps)
        self.assertTrue("bar" in result.unused_deps)
        self.assertTrue("impl_foo" in result.unused_implementation_deps)
        self.assertTrue("impl_bar" in result.unused_implementation_deps)

    def test_public_dependencies_which_should_be_private(self):
        result = evaluate_includes(
            public_includes=[Include(file=Path("public_file"), include="foobar.h")],
            private_includes=[
                Include(file=Path("private_file"), include="impl_dep_foo.h"),
                Include(file=Path("private_file"), include="impl_dep_bar.h"),
            ],
            system_under_inspection=SystemUnderInspection(
                target_under_inspection=CcTarget(name="foo", header_files=[]),
                deps=[
                    CcTarget(name="foobar", header_files=["foobar.h"]),
                    CcTarget(name="foo", header_files=["impl_dep_foo.h"]),
                    CcTarget(name="bar", header_files=["impl_dep_bar.h"]),
                ],
                implementation_deps=[],
                include_paths=[""],
                defines=[],
            ),
            ensure_private_deps=True,
        )

        self.assertFalse(result.is_ok())
        self.assertEqual(result.public_includes_without_dep, [])
        self.assertEqual(result.private_includes_without_dep, [])
        self.assertEqual(result.unused_deps, [])
        self.assertEqual(result.unused_implementation_deps, [])
        self.assertEqual(len(result.deps_which_should_be_private), 2)
        self.assertTrue("foo" in result.deps_which_should_be_private)
        self.assertTrue("bar" in result.deps_which_should_be_private)

    def test_public_dependencies_which_should_be_private_disabled(self):
        result = evaluate_includes(
            public_includes=[Include(file=Path("public_file"), include="foobar.h")],
            private_includes=[
                Include(file=Path("private_file"), include="impl_dep_foo.h"),
                Include(file=Path("private_file"), include="impl_dep_bar.h"),
            ],
            system_under_inspection=SystemUnderInspection(
                target_under_inspection=CcTarget(name="foo", header_files=[]),
                deps=[
                    CcTarget(name="foobar", header_files=["foobar.h"]),
                    CcTarget(name="foo", header_files=["impl_dep_foo.h"]),
                    CcTarget(name="bar", header_files=["impl_dep_bar.h"]),
                ],
                implementation_deps=[],
                include_paths=[""],
                defines=[],
            ),
            ensure_private_deps=False,
        )

        self.assertTrue(result.is_ok())


if __name__ == "__main__":
    unittest.main()
