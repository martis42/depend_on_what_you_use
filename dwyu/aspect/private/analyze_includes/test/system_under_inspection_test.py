import unittest
from pathlib import Path

from dwyu.aspect.private.analyze_includes.system_under_inspection import (
    CcTarget,
    UsageStatus,
    UsageStatusTracker,
    get_system_under_inspection,
)

TEST_DATA = Path("dwyu/aspect/private/analyze_includes/test/data")


class TestUsageStatusTracker(unittest.TestCase):
    @staticmethod
    def make_tracker_with_value(value: UsageStatus) -> UsageStatusTracker:
        unit = UsageStatusTracker()
        unit.update(value)
        return unit

    def test_default_ctor(self) -> None:
        unit = UsageStatusTracker()

        self.assertEqual(unit.usage, UsageStatus.NONE)
        self.assertFalse(unit.is_used())

    def test_no_usage_resetting(self) -> None:
        unit = UsageStatusTracker()
        with self.assertRaisesRegex(Exception, "Resetting the usage is not supported"):
            unit.update(UsageStatus.NONE)

    def test_update_to_public_and_then_private(self) -> None:
        unit = UsageStatusTracker()

        unit.update(UsageStatus.PUBLIC)
        self.assertEqual(unit.usage, UsageStatus.PUBLIC)

        unit.update(UsageStatus.PRIVATE)
        self.assertEqual(unit.usage, UsageStatus.PUBLIC_AND_PRIVATE)

    def test_update_to_private_and_then_public(self) -> None:
        unit = UsageStatusTracker()

        unit.update(UsageStatus.PRIVATE)
        self.assertEqual(unit.usage, UsageStatus.PRIVATE)

        unit.update(UsageStatus.PUBLIC)
        self.assertEqual(unit.usage, UsageStatus.PUBLIC_AND_PRIVATE)

    def test_public_and_private_state_is_stable(self) -> None:
        unit = self.make_tracker_with_value(UsageStatus.PUBLIC_AND_PRIVATE)

        unit.update(UsageStatus.PUBLIC)
        self.assertEqual(unit.usage, UsageStatus.PUBLIC_AND_PRIVATE)

        unit.update(UsageStatus.PRIVATE)
        self.assertEqual(unit.usage, UsageStatus.PUBLIC_AND_PRIVATE)

        unit.update(UsageStatus.PUBLIC_AND_PRIVATE)
        self.assertEqual(unit.usage, UsageStatus.PUBLIC_AND_PRIVATE)

    def test_repr(self) -> None:
        unit_a = UsageStatusTracker()
        self.assertEqual(repr(unit_a), "NONE")

        unit_b = self.make_tracker_with_value(UsageStatus.PUBLIC)
        self.assertEqual(repr(unit_b), "PUBLIC")

        unit_c = self.make_tracker_with_value(UsageStatus.PRIVATE)
        self.assertEqual(repr(unit_c), "PRIVATE")

        unit_d = self.make_tracker_with_value(UsageStatus.PUBLIC_AND_PRIVATE)
        self.assertEqual(repr(unit_d), "PUBLIC_AND_PRIVATE")


class TestCcTarget(unittest.TestCase):
    def test_repr(self) -> None:
        unit = CcTarget(name="//:foo", header_files=["bar.h"])

        self.assertEqual(repr(unit), "CcTarget(name='//:foo', usage='NONE', header_files=['bar.h'])")


class TestGetSystemUnderInspection(unittest.TestCase):
    def test_load_full_file(self) -> None:
        sui = get_system_under_inspection(
            target_under_inspection=TEST_DATA / "target_under_inspection.json",
            deps=[TEST_DATA / "dep_info_foo.json", TEST_DATA / "dep_info_bar.json"],
            impl_deps=[TEST_DATA / "implementation_dep_info_foo.json", TEST_DATA / "implementation_dep_info_bar.json"],
        )

        self.assertEqual(sui.target_under_inspection.name, "//:baz")
        self.assertEqual(sui.target_under_inspection.header_files, ["self/header_1.h", "self/header_2.h"])
        self.assertEqual(sui.target_under_inspection.usage.usage, UsageStatus.NONE)

        self.assertEqual(len(sui.deps), 2)
        self.assertEqual(sui.deps[0].name, "//public/dep:foo")
        self.assertEqual(sui.deps[0].header_files, ["public/dep/foo_1.h", "public/dep/foo_2.h"])
        self.assertEqual(sui.deps[0].usage.usage, UsageStatus.NONE)
        self.assertEqual(sui.deps[1].name, "//public/dep:bar")
        self.assertEqual(sui.deps[1].header_files, ["public/dep/bar_1.h", "public/dep/bar_2.h"])
        self.assertEqual(sui.deps[1].usage.usage, UsageStatus.NONE)

        self.assertEqual(len(sui.impl_deps), 2)
        self.assertEqual(sui.impl_deps[0].name, "//private/dep:foo")
        self.assertEqual(sui.impl_deps[0].header_files, ["private/dep/foo_1.h", "private/dep/foo_2.h"])
        self.assertEqual(sui.impl_deps[0].usage.usage, UsageStatus.NONE)
        self.assertEqual(sui.impl_deps[1].name, "//private/dep:bar")
        self.assertEqual(sui.impl_deps[1].header_files, ["private/dep/bar_1.h", "private/dep/bar_2.h"])
        self.assertEqual(sui.impl_deps[1].usage.usage, UsageStatus.NONE)

        self.assertEqual(sui.include_paths, ["", "some/dir", "external/dir", "another/dir"])
        self.assertEqual(sui.defines, ["SOME_DEFINE", "ANOTHER_DEFINE 42"])

    def test_load_empty_file(self) -> None:
        sui = get_system_under_inspection(
            target_under_inspection=TEST_DATA / "target_under_inspection_empty.json", deps=[], impl_deps=[]
        )

        self.assertEqual(sui.target_under_inspection.name, "//:foo")
        self.assertEqual(sui.target_under_inspection.header_files, [])
        self.assertEqual(sui.target_under_inspection.usage.usage, UsageStatus.NONE)
        self.assertEqual(sui.deps, [])
        self.assertEqual(sui.impl_deps, [])
        self.assertEqual(sui.include_paths, [])
        self.assertEqual(sui.defines, [])


if __name__ == "__main__":
    unittest.main()
