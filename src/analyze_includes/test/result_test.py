import unittest
from pathlib import Path

from src.analyze_includes.parse_source import Include
from src.analyze_includes.result import Result


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
  "unused_deps": [],
  "unused_implementation_deps": [],
  "deps_which_should_be_private": [],
  "use_implementation_deps": false
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
  "unused_deps": [],
  "unused_implementation_deps": [],
  "deps_which_should_be_private": [],
  "use_implementation_deps": false
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
  "unused_deps": [],
  "unused_implementation_deps": [],
  "deps_which_should_be_private": [],
  "use_implementation_deps": false
}
""".lstrip(),
        )

    def test_is_ok_fails_due_to_unused_public_deps(self):
        unit = Result(target="//foo:bar", unused_deps=["foo", "baz"])

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
  "unused_deps": [
    "foo",
    "baz"
  ],
  "unused_implementation_deps": [],
  "deps_which_should_be_private": [],
  "use_implementation_deps": false
}
""".lstrip(),
        )

    def test_is_ok_fails_due_to_unused_private_deps(self):
        unit = Result(target="//foo:bar", unused_implementation_deps=["foo", "baz"])

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
  "unused_deps": [],
  "unused_implementation_deps": [
    "foo",
    "baz"
  ],
  "deps_which_should_be_private": [],
  "use_implementation_deps": false
}
""".lstrip(),
        )

    def test_is_ok_fails_due_to_unused_public_and_private_deps(self):
        unit = Result(target="//foo:bar", unused_deps=["foo"], unused_implementation_deps=["baz"])

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
  "unused_deps": [
    "foo"
  ],
  "unused_implementation_deps": [
    "baz"
  ],
  "deps_which_should_be_private": [],
  "use_implementation_deps": false
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
  "unused_deps": [],
  "unused_implementation_deps": [],
  "deps_which_should_be_private": [
    "foo",
    "baz"
  ],
  "use_implementation_deps": false
}
""".lstrip(),
        )


def test_set_use_implementation_deps(self):
    unit = Result(target="//:foo", use_implementation_deps=True)

    self.assertEqual(
        unit.to_json(),
        """
{
"analyzed_target": "//:foo",
"public_includes_without_dep": {},
"private_includes_without_dep": {},
"unused_deps": [],
"unused_implementation_deps": [],
"deps_which_should_be_private": [],
"use_implementation_deps": false
}
""".lstrip(),
    )


if __name__ == "__main__":
    unittest.main()
