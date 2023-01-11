import unittest
from pathlib import Path

from src.analyze_includes.get_dependencies import (
    AvailableDependency,
    AvailableInclude,
    IncludeUsage,
    get_available_dependencies,
)


class TestAvailableInclude(unittest.TestCase):
    def test_default_ctor(self):
        unit = AvailableInclude(hdr="hdr")

        self.assertEqual(unit.used, IncludeUsage.NONE)

    def test_equality(self):
        unit_a = AvailableInclude(hdr="hdr_1", used=IncludeUsage.PUBLIC)
        unit_b = AvailableInclude(hdr="hdr_1", used=IncludeUsage.PUBLIC)
        unit_c = AvailableInclude(hdr="hdr_1", used=IncludeUsage.PRIVATE)
        unit_d = AvailableInclude(hdr="hdr_2", used=IncludeUsage.PUBLIC)

        self.assertEqual(unit_a, unit_b)
        self.assertNotEqual(unit_a, unit_c)
        self.assertNotEqual(unit_a, unit_d)
        self.assertNotEqual(unit_c, unit_d)

    def test_repr(self):
        unit_a = AvailableInclude(hdr="foo", used=IncludeUsage.NONE)
        self.assertEqual(repr(unit_a), "AvailableInclude(hdr='foo', used='NONE')")

        unit_b = AvailableInclude(hdr="bar", used=IncludeUsage.PUBLIC)
        self.assertEqual(repr(unit_b), "AvailableInclude(hdr='bar', used='PUBLIC')")

        unit_c = AvailableInclude(hdr="baz", used=IncludeUsage.PRIVATE)
        self.assertEqual(repr(unit_c), "AvailableInclude(hdr='baz', used='PRIVATE')")

        unit_d = AvailableInclude(hdr="barbaz", used=IncludeUsage.PUBLIC_AND_PRIVATE)
        self.assertEqual(repr(unit_d), "AvailableInclude(hdr='barbaz', used='PUBLIC_AND_PRIVATE')")

    def test_make_public(self):
        unit = AvailableInclude(hdr="hdr", used=IncludeUsage.NONE)
        unit.update_usage(IncludeUsage.PUBLIC)

        self.assertEqual(unit.used, IncludeUsage.PUBLIC)

    def test_make_private(self):
        unit = AvailableInclude(hdr="hdr", used=IncludeUsage.NONE)
        unit.update_usage(IncludeUsage.PRIVATE)

        self.assertEqual(unit.used, IncludeUsage.PRIVATE)

    def test_make_public_and_private(self):
        unit = AvailableInclude(hdr="hdr", used=IncludeUsage.NONE)
        unit.update_usage(IncludeUsage.PUBLIC_AND_PRIVATE)

        self.assertEqual(unit.used, IncludeUsage.PUBLIC_AND_PRIVATE)

    def test_add_private_to_public(self):
        unit = AvailableInclude(hdr="hdr", used=IncludeUsage.PUBLIC)
        unit.update_usage(IncludeUsage.PRIVATE)

        self.assertEqual(unit.used, IncludeUsage.PUBLIC_AND_PRIVATE)

    def test_add_public_to_private(self):
        unit = AvailableInclude(hdr="hdr", used=IncludeUsage.PRIVATE)
        unit.update_usage(IncludeUsage.PUBLIC)

        self.assertEqual(unit.used, IncludeUsage.PUBLIC_AND_PRIVATE)

    def test_public_and_private_state_is_stable(self):
        unit = AvailableInclude(hdr="hdr", used=IncludeUsage.PUBLIC_AND_PRIVATE)

        unit.update_usage(IncludeUsage.PUBLIC)
        self.assertEqual(unit.used, IncludeUsage.PUBLIC_AND_PRIVATE)

        unit.update_usage(IncludeUsage.PRIVATE)
        self.assertEqual(unit.used, IncludeUsage.PUBLIC_AND_PRIVATE)

        unit.update_usage(IncludeUsage.PUBLIC_AND_PRIVATE)
        self.assertEqual(unit.used, IncludeUsage.PUBLIC_AND_PRIVATE)

    def test_no_usage_resetting(self):
        unit = AvailableInclude(hdr="hdr")
        with self.assertRaises(Exception):
            unit.update_usage(IncludeUsage.NONE)


class TestAvailableDependency(unittest.TestCase):
    def test_repr(self):
        header_a = AvailableInclude(hdr="foo.h", used=IncludeUsage.NONE)
        header_b = AvailableInclude(hdr="bar.h", used=IncludeUsage.PUBLIC)

        unit = AvailableDependency("//baz", [header_a, header_b])

        self.assertEqual(
            repr(unit),
            "AvailableDependency(name='//baz', hdrs=[AvailableInclude(hdr='foo.h', used='NONE'), AvailableInclude(hdr='bar.h', used='PUBLIC')])",
        )


class TestGetAvailableDependencies(unittest.TestCase):
    def test_load_full_file(self):
        deps = get_available_dependencies(Path("src/analyze_includes/test/data/deps_info_full.json"))

        self.assertEqual(len(deps.private), 2)
        self.assertEqual(len(deps.public), 2)

        self.assertEqual(deps.private[0].name, "//private/dep:foo")
        self.assertEqual(
            deps.private[0].hdrs, [AvailableInclude("private/dep/foo_a.h"), AvailableInclude("private/dep/foo_b.h")]
        )
        self.assertEqual(deps.private[1].name, "//private/dep:bar")
        self.assertEqual(
            deps.private[1].hdrs, [AvailableInclude("private/dep/bar_a.h"), AvailableInclude("private/dep/bar_b.h")]
        )

        self.assertEqual(deps.public[0].name, "//public/dep:foo")
        self.assertEqual(
            deps.public[0].hdrs, [AvailableInclude("public/dep/foo_a.h"), AvailableInclude("public/dep/foo_b.h")]
        )
        self.assertEqual(deps.public[1].name, "//public/dep:bar")
        self.assertEqual(
            deps.public[1].hdrs, [AvailableInclude("public/dep/bar_a.h"), AvailableInclude("public/dep/bar_b.h")]
        )

        self.assertEqual(len(deps.own_hdrs), 2)
        self.assertEqual(deps.own_hdrs, [AvailableInclude("self/a.h"), AvailableInclude("self/b.h")])

    def test_load_empty_file(self):
        deps = get_available_dependencies(Path("src/analyze_includes/test/data/deps_info_empty.json"))

        self.assertEqual(len(deps.private), 0)
        self.assertEqual(len(deps.public), 0)

        self.assertEqual(len(deps.own_hdrs), 0)


if __name__ == "__main__":
    unittest.main()
