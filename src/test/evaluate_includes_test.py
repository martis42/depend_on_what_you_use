import unittest
from pathlib import Path

from src.evaluate_includes import Result, evaluate_includes
from src.get_dependencies import (
    AvailableDependencies,
    AvailableDependency,
    AvailableInclude,
)
from src.parse_source import Include


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

    @staticmethod
    def _expected_json(target: str, includes_error="", unused_error="", should_be_private_error="") -> str:
        def _dict_error(msg: str) -> str:
            if msg:
                return "{\n" + 2 * indent + msg + "\n" + indent + "}"
            return "{}"

        def _list_error(msg: str) -> str:
            if msg:
                return "[\n" + 2 * indent + msg + "\n" + indent + "]"
            return "[]"

        indent = 2 * " "
        content = indent + f'"analyzed_target": "{target}",\n'
        content += indent + f'"invalid_includes": {_dict_error(includes_error)},\n'
        content += indent + f'"unused_dependencies": {_list_error(unused_error)},\n'
        content += indent + f'"deps_which_should_be_private": {_list_error(should_be_private_error)}'

        return "{\n" + content + "\n}\n"

    def test_is_ok(self):
        unit = Result("//foo:bar")

        self.assertTrue(unit.is_ok())
        self.assertEqual(unit.to_str(), self._expected_msg(target="//foo:bar"))
        self.assertEqual(unit.to_json(), self._expected_json(target="//foo:bar"))

    def test_is_ok_fails_due_to_invalid_includes(self):
        unit = Result(target="//foo:bar", invalid_includes=[Include(file=Path("foo"), include="bar")])

        self.assertFalse(unit.is_ok())
        self.assertEqual(
            unit.to_str(),
            self._expected_msg(
                target="//foo:bar",
                errors="Includes which are not available from the direct dependencies:\n" "  File='foo', include='bar'",
            ),
        )
        self.assertEqual(unit.to_json(), self._expected_json(target="//foo:bar", includes_error='"foo": "bar"'))

    def test_is_ok_fails_due_to_unused_deps(self):
        unit = Result(target="//foo:bar", unused_deps=["foo"])

        self.assertFalse(unit.is_ok())
        self.assertEqual(
            unit.to_str(),
            self._expected_msg(
                target="//foo:bar",
                errors="Unused dependencies (none of their headers are referenced):\n  Dependency='foo'",
            ),
        )
        self.assertEqual(unit.to_json(), self._expected_json(target="//foo:bar", unused_error='"foo"'))

    def test_is_ok_fails_due_to_deps_which_should_be_private(self):
        unit = Result(target="//foo:bar", deps_which_should_be_private=["foo"])

        self.assertFalse(unit.is_ok())
        self.assertEqual(
            unit.to_str(),
            self._expected_msg(
                target="//foo:bar",
                errors="Public dependencies which are only used in private code, move them to 'implementation_deps':\n"
                "  Dependency='foo'",
            ),
        )
        self.assertEqual(unit.to_json(), self._expected_json(target="//foo:bar", should_be_private_error='"foo"'))


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
                self=AvailableDependency(name="self", hdrs=[AvailableInclude("self/own_header.h")]),
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
                self=AvailableDependency(name="", hdrs=[AvailableInclude("foo.h"), AvailableInclude("bar.h")]),
                public=[],
                private=[],
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
                self=AvailableDependency(
                    name="self",
                    hdrs=[
                        AvailableInclude("nested/dir/foo.h"),
                        AvailableInclude("nested/dir/bar.h"),
                        AvailableInclude("nested/dir/sub/baz.h"),
                    ],
                ),
                public=[],
                private=[],
            ),
            ensure_private_deps=True,
        )

        self.assertTrue(result.is_ok())

    def test_invalid_includes_missing_internal_include(self):
        result = evaluate_includes(
            target="foo",
            public_includes=[Include(file=Path("nested/dir/foo.h"), include="bar.h")],
            private_includes=[],
            dependencies=AvailableDependencies(
                self=AvailableDependency(
                    name="self", hdrs=[AvailableInclude("nested/dir/foo.h"), AvailableInclude("some/other/dir/bar.h")]
                ),
                public=[],
                private=[],
            ),
            ensure_private_deps=True,
        )

        self.assertFalse(result.is_ok())
        self.assertEqual(result.unused_deps, [])
        self.assertEqual(result.deps_which_should_be_private, [])
        self.assertEqual(result.invalid_includes, [Include(file=Path("nested/dir/foo.h"), include="bar.h")])

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
                self=AvailableDependency(name="", hdrs=[]),
                public=[AvailableDependency(name="foo", hdrs=[AvailableInclude("foo.h")])],
                private=[AvailableDependency(name="bar", hdrs=[AvailableInclude("bar.h")])],
            ),
            ensure_private_deps=True,
        )

        self.assertFalse(result.is_ok())
        self.assertEqual(result.unused_deps, [])
        self.assertEqual(result.deps_which_should_be_private, [])
        self.assertEqual(len(result.invalid_includes), 4)
        self.assertTrue(Include(file=Path("public_file"), include="foo/foo.h") in result.invalid_includes)
        self.assertTrue(Include(file=Path("public_file"), include="foo/bar.h") in result.invalid_includes)
        self.assertTrue(Include(file=Path("private_file"), include="bar/foo.h") in result.invalid_includes)
        self.assertTrue(Include(file=Path("private_file"), include="bar/bar.h") in result.invalid_includes)

    def test_unused_dependencies(self):
        result = evaluate_includes(
            target="foo",
            public_includes=[Include(file=Path("public_file"), include="foobar.h")],
            private_includes=[Include(file=Path("private_file"), include="impl_dep.h")],
            dependencies=AvailableDependencies(
                self=AvailableDependency(name="", hdrs=[]),
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
        self.assertEqual(result.invalid_includes, [])
        self.assertEqual(result.deps_which_should_be_private, [])
        self.assertEqual(len(result.unused_deps), 4)
        self.assertTrue("foo" in result.unused_deps)
        self.assertTrue("bar" in result.unused_deps)
        self.assertTrue("impl_foo" in result.unused_deps)
        self.assertTrue("impl_bar" in result.unused_deps)

    def test_public_dependencies_which_should_be_private(self):
        result = evaluate_includes(
            target="foo",
            public_includes=[Include(file=Path("public_file"), include="foobar.h")],
            private_includes=[
                Include(file=Path("private_file"), include="impl_dep_foo.h"),
                Include(file=Path("private_file"), include="impl_dep_bar.h"),
            ],
            dependencies=AvailableDependencies(
                self=AvailableDependency(name="", hdrs=[]),
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
        self.assertEqual(result.invalid_includes, [])
        self.assertEqual(result.unused_deps, [])
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
                self=AvailableDependency(name="", hdrs=[]),
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
