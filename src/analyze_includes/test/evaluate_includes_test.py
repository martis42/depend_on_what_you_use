import unittest
from pathlib import Path

from src.analyze_includes.evaluate_includes import Result, evaluate_includes
from src.analyze_includes.get_dependencies import (
    AvailableDependencies,
    AvailableDependency,
    AvailableInclude,
)
from src.analyze_includes.parse_source import Include


class TestResult(unittest.TestCase):
    @staticmethod
    def _expected_msg(target: str, errors: str = "") -> str:
        border = 80 * "="
        msg = f"DWYU analyzing: '{target}'\n\n"
        if errors:
            msg += "Result: FAILURE\n\n"
        else:
            msg += "Result: SUCCESS"
        return border + "\n" + msg + errors + "\n" + border

    def test_is_ok(self):
        unit = Result("//foo:bar")

        self.assertTrue(unit.is_ok())
        self.assertEqual(unit.to_str(), self._expected_msg(target="//foo:bar"))
        self.assertEqual(
            unit.to_json(),
            """
{
  "analyzed_target": "//foo:bar",
  "public_includes_without_dep": {},
  "private_includes_without_dep": {},
  "unused_public_deps": [],
  "unused_private_deps": [],
  "deps_which_should_be_private": []
}
""".lstrip(),
        )

    def test_is_ok_fails_due_to_invalid_private_includes(self):
        unit = Result(
            target="//foo:bar",
            private_includes_without_dep=[
                Include(file=Path("foo"), include="missing_1"),
                Include(file=Path("bar"), include="missing_2"),
                Include(file=Path("bar"), include="missing_3"),
            ],
        )

        self.assertFalse(unit.is_ok())
        self.assertEqual(
            unit.to_str(),
            self._expected_msg(
                target="//foo:bar",
                errors="Includes which are not available from the direct dependencies:\n"
                "  File='foo', include='missing_1'\n"
                "  File='bar', include='missing_2'\n"
                "  File='bar', include='missing_3'",
            ),
        )
        self.assertEqual(
            unit.to_json(),
            """
{
  "analyzed_target": "//foo:bar",
  "public_includes_without_dep": {},
  "private_includes_without_dep": {
    "foo": [
      "missing_1"
    ],
    "bar": [
      "missing_2",
      "missing_3"
    ]
  },
  "unused_public_deps": [],
  "unused_private_deps": [],
  "deps_which_should_be_private": []
}
""".lstrip(),
        )

    def test_is_ok_fails_due_to_invalid_public_includes(self):
        unit = Result(
            target="//foo:bar",
            public_includes_without_dep=[
                Include(file=Path("foo"), include="missing_1"),
                Include(file=Path("bar"), include="missing_2"),
                Include(file=Path("bar"), include="missing_3"),
            ],
        )

        self.assertFalse(unit.is_ok())
        self.assertEqual(
            unit.to_str(),
            self._expected_msg(
                target="//foo:bar",
                errors="Includes which are not available from the direct dependencies:\n"
                "  File='foo', include='missing_1'\n"
                "  File='bar', include='missing_2'\n"
                "  File='bar', include='missing_3'",
            ),
        )
        self.assertEqual(
            unit.to_json(),
            """
{
  "analyzed_target": "//foo:bar",
  "public_includes_without_dep": {
    "foo": [
      "missing_1"
    ],
    "bar": [
      "missing_2",
      "missing_3"
    ]
  },
  "private_includes_without_dep": {},
  "unused_public_deps": [],
  "unused_private_deps": [],
  "deps_which_should_be_private": []
}
""".lstrip(),
        )

    def test_is_ok_fails_due_to_unused_public_deps(self):
        unit = Result(target="//foo:bar", unused_public_deps=["foo", "baz"])

        self.assertFalse(unit.is_ok())
        self.assertEqual(
            unit.to_str(),
            self._expected_msg(
                target="//foo:bar",
                errors="Unused dependencies in 'deps' (none of their headers are referenced):\n"
                "  Dependency='foo'\n"
                "  Dependency='baz'",
            ),
        )
        self.assertEqual(
            unit.to_json(),
            """
{
  "analyzed_target": "//foo:bar",
  "public_includes_without_dep": {},
  "private_includes_without_dep": {},
  "unused_public_deps": [
    "foo",
    "baz"
  ],
  "unused_private_deps": [],
  "deps_which_should_be_private": []
}
""".lstrip(),
        )

    def test_is_ok_fails_due_to_unused_private_deps(self):
        unit = Result(target="//foo:bar", unused_private_deps=["foo", "baz"])

        self.assertFalse(unit.is_ok())
        self.assertEqual(
            unit.to_str(),
            self._expected_msg(
                target="//foo:bar",
                errors="Unused dependencies in 'implementation_deps' (none of their headers are referenced):\n"
                "  Dependency='foo'\n"
                "  Dependency='baz'",
            ),
        )
        self.assertEqual(
            unit.to_json(),
            """
{
  "analyzed_target": "//foo:bar",
  "public_includes_without_dep": {},
  "private_includes_without_dep": {},
  "unused_public_deps": [],
  "unused_private_deps": [
    "foo",
    "baz"
  ],
  "deps_which_should_be_private": []
}
""".lstrip(),
        )

    def test_is_ok_fails_due_to_unused_public_and_private_deps(self):
        unit = Result(target="//foo:bar", unused_public_deps=["foo"], unused_private_deps=["baz"])

        self.assertFalse(unit.is_ok())
        self.assertEqual(
            unit.to_str(),
            self._expected_msg(
                target="//foo:bar",
                errors="Unused dependencies in 'deps' (none of their headers are referenced):\n"
                "  Dependency='foo'\n"
                "Unused dependencies in 'implementation_deps' (none of their headers are referenced):\n"
                "  Dependency='baz'",
            ),
        )
        self.assertEqual(
            unit.to_json(),
            """
{
  "analyzed_target": "//foo:bar",
  "public_includes_without_dep": {},
  "private_includes_without_dep": {},
  "unused_public_deps": [
    "foo"
  ],
  "unused_private_deps": [
    "baz"
  ],
  "deps_which_should_be_private": []
}
""".lstrip(),
        )

    def test_is_ok_fails_due_to_deps_which_should_be_private(self):
        unit = Result(target="//foo:bar", deps_which_should_be_private=["foo", "baz"])

        self.assertFalse(unit.is_ok())
        self.assertEqual(
            unit.to_str(),
            self._expected_msg(
                target="//foo:bar",
                errors="Public dependencies which are used only in private code:\n"
                "  Dependency='foo'\n"
                "  Dependency='baz'",
            ),
        )
        self.assertEqual(
            unit.to_json(),
            """
{
  "analyzed_target": "//foo:bar",
  "public_includes_without_dep": {},
  "private_includes_without_dep": {},
  "unused_public_deps": [],
  "unused_private_deps": [],
  "deps_which_should_be_private": [
    "foo",
    "baz"
  ]
}
""".lstrip(),
        )


class TestEvaluateIncludes(unittest.TestCase):
    def test_success_for_valid_external_dependencies(self):
        result = evaluate_includes(
            target="foo",
            public_includes=[
                Include(file=Path("file1"), include="foo.h"),
                Include(file=Path("file2"), include="foo/bar.h"),
            ],
            private_includes=[
                Include(file=Path("file3"), include="baz.h"),
                Include(file=Path("file4"), include="self/own_header.h"),
            ],
            dependencies=AvailableDependencies(
                own_hdrs=[AvailableInclude("self/own_header.h")],
                public=[
                    AvailableDependency(
                        name="foo_pkg", hdrs=[AvailableInclude("foo.h"), AvailableInclude("foo/bar.h")]
                    ),
                    AvailableDependency(name="lib_without_hdrs_purely_for_linking", hdrs=[]),
                ],
                private=[AvailableDependency(name="baz_pkg", hdrs=[AvailableInclude("baz.h")])],
            ),
            ensure_private_deps=True,
        )

        self.assertTrue(result.is_ok())

    def test_success_for_target_internal_includes_with_flat_structure(self):
        result = evaluate_includes(
            target="foo",
            public_includes=[Include(file=Path("foo.h"), include="bar.h")],
            private_includes=[],
            dependencies=AvailableDependencies(
                own_hdrs=[AvailableInclude("foo.h"), AvailableInclude("bar.h")], public=[], private=[]
            ),
            ensure_private_deps=True,
        )

        self.assertTrue(result.is_ok())

    def test_success_for_target_internal_includes_with_nested_structure(self):
        result = evaluate_includes(
            target="foo",
            public_includes=[
                Include(file=Path("nested/dir/foo.h"), include="bar.h"),
                Include(file=Path("nested/dir/foo.h"), include="sub/baz.h"),
            ],
            private_includes=[],
            dependencies=AvailableDependencies(
                own_hdrs=[
                    AvailableInclude("nested/dir/foo.h"),
                    AvailableInclude("nested/dir/bar.h"),
                    AvailableInclude("nested/dir/sub/baz.h"),
                ],
                public=[],
                private=[],
            ),
            ensure_private_deps=True,
        )

        self.assertTrue(result.is_ok())

    def test_invalid_includes_missing_internal_include(self):
        result = evaluate_includes(
            target="foo",
            public_includes=[Include(file=Path("some/dir/foo.h"), include="tick.h")],
            private_includes=[Include(file=Path("some/dir/bar.h"), include="tock.h")],
            # Make sure files with the required name which are at the wrong location are ignored
            dependencies=AvailableDependencies(
                own_hdrs=[
                    AvailableInclude("some/dir/foo.h"),
                    AvailableInclude("some/dir/bar.h"),
                    AvailableInclude("unrelated/dir/tick.h"),
                    AvailableInclude("unrelated/dir/tock.h"),
                ],
                public=[],
                private=[],
            ),
            ensure_private_deps=True,
        )

        self.assertFalse(result.is_ok())
        self.assertEqual(result.unused_public_deps, [])
        self.assertEqual(result.unused_private_deps, [])
        self.assertEqual(result.deps_which_should_be_private, [])
        self.assertEqual(result.public_includes_without_dep, [Include(file=Path("some/dir/foo.h"), include="tick.h")])
        self.assertEqual(result.private_includes_without_dep, [Include(file=Path("some/dir/bar.h"), include="tock.h")])

    def test_missing_includes_from_dependencies(self):
        result = evaluate_includes(
            target="foo",
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
            dependencies=AvailableDependencies(
                own_hdrs=[],
                public=[AvailableDependency(name="foo", hdrs=[AvailableInclude("foo.h")])],
                private=[AvailableDependency(name="bar", hdrs=[AvailableInclude("bar.h")])],
            ),
            ensure_private_deps=True,
        )

        self.assertFalse(result.is_ok())
        self.assertEqual(result.unused_public_deps, [])
        self.assertEqual(result.unused_private_deps, [])
        self.assertEqual(result.deps_which_should_be_private, [])
        self.assertEqual(len(result.public_includes_without_dep), 2)
        self.assertTrue(Include(file=Path("public_file"), include="foo/foo.h") in result.public_includes_without_dep)
        self.assertTrue(Include(file=Path("public_file"), include="foo/bar.h") in result.public_includes_without_dep)
        self.assertEqual(len(result.private_includes_without_dep), 2)
        self.assertTrue(Include(file=Path("private_file"), include="bar/foo.h") in result.private_includes_without_dep)
        self.assertTrue(Include(file=Path("private_file"), include="bar/bar.h") in result.private_includes_without_dep)

    def test_unused_dependencies(self):
        result = evaluate_includes(
            target="foo",
            public_includes=[Include(file=Path("public_file"), include="foobar.h")],
            private_includes=[Include(file=Path("private_file"), include="impl_dep.h")],
            dependencies=AvailableDependencies(
                own_hdrs=[],
                public=[
                    AvailableDependency(name="foobar", hdrs=[AvailableInclude("foobar.h")]),
                    AvailableDependency(name="foo", hdrs=[AvailableInclude("foo.h")]),
                    AvailableDependency(name="bar", hdrs=[AvailableInclude("bar.h")]),
                ],
                private=[
                    AvailableDependency(name="impl_dep", hdrs=[AvailableInclude("impl_dep.h")]),
                    AvailableDependency(name="impl_foo", hdrs=[AvailableInclude("impl_dep_foo.h")]),
                    AvailableDependency(name="impl_bar", hdrs=[AvailableInclude("impl_dep_bar.h")]),
                ],
            ),
            ensure_private_deps=True,
        )

        self.assertFalse(result.is_ok())
        self.assertEqual(result.public_includes_without_dep, [])
        self.assertEqual(result.private_includes_without_dep, [])
        self.assertEqual(result.deps_which_should_be_private, [])
        self.assertEqual(len(result.unused_public_deps), 2)
        self.assertEqual(len(result.unused_private_deps), 2)
        self.assertTrue("foo" in result.unused_public_deps)
        self.assertTrue("bar" in result.unused_public_deps)
        self.assertTrue("impl_foo" in result.unused_private_deps)
        self.assertTrue("impl_bar" in result.unused_private_deps)

    def test_public_dependencies_which_should_be_private(self):
        result = evaluate_includes(
            target="foo",
            public_includes=[Include(file=Path("public_file"), include="foobar.h")],
            private_includes=[
                Include(file=Path("private_file"), include="impl_dep_foo.h"),
                Include(file=Path("private_file"), include="impl_dep_bar.h"),
            ],
            dependencies=AvailableDependencies(
                own_hdrs=[],
                public=[
                    AvailableDependency(name="foobar", hdrs=[AvailableInclude("foobar.h")]),
                    AvailableDependency(name="foo", hdrs=[AvailableInclude("impl_dep_foo.h")]),
                    AvailableDependency(name="bar", hdrs=[AvailableInclude("impl_dep_bar.h")]),
                ],
                private=[],
            ),
            ensure_private_deps=True,
        )

        self.assertFalse(result.is_ok())
        self.assertEqual(result.public_includes_without_dep, [])
        self.assertEqual(result.private_includes_without_dep, [])
        self.assertEqual(result.unused_public_deps, [])
        self.assertEqual(result.unused_private_deps, [])
        self.assertEqual(len(result.deps_which_should_be_private), 2)
        self.assertTrue("foo" in result.deps_which_should_be_private)
        self.assertTrue("bar" in result.deps_which_should_be_private)

    def test_public_dependencies_which_should_be_private_disabled(self):
        result = evaluate_includes(
            target="foo",
            public_includes=[Include(file=Path("public_file"), include="foobar.h")],
            private_includes=[
                Include(file=Path("private_file"), include="impl_dep_foo.h"),
                Include(file=Path("private_file"), include="impl_dep_bar.h"),
            ],
            dependencies=AvailableDependencies(
                own_hdrs=[],
                public=[
                    AvailableDependency(name="foobar", hdrs=[AvailableInclude("foobar.h")]),
                    AvailableDependency(name="foo", hdrs=[AvailableInclude("impl_dep_foo.h")]),
                    AvailableDependency(name="bar", hdrs=[AvailableInclude("impl_dep_bar.h")]),
                ],
                private=[],
            ),
            ensure_private_deps=False,
        )

        self.assertTrue(result.is_ok())


if __name__ == "__main__":
    unittest.main()
