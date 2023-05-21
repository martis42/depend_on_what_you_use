import unittest
from pathlib import Path
from typing import List

from src.analyze_includes.system_under_inspection import (
    CcTarget,
    HeaderFile,
    IncludePath,
    UsageStatus,
    UsageStatusTracker,
    get_system_under_inspection,
)


class TestUsageStatusTracker(unittest.TestCase):
    @staticmethod
    def make_tracker_with_value(value: UsageStatus) -> UsageStatusTracker:
        unit = UsageStatusTracker()
        unit.update(value)
        return unit

    def test_default_ctor(self):
        unit = UsageStatusTracker()

        self.assertEqual(unit.usage, UsageStatus.NONE)
        self.assertFalse(unit.is_used())

    def test_no_usage_resetting(self):
        unit = UsageStatusTracker()
        with self.assertRaises(Exception):
            unit.update(UsageStatus.NONE)

    def test_update_to_public_and_then_private(self):
        unit = UsageStatusTracker()

        unit.update(UsageStatus.PUBLIC)
        self.assertEqual(unit.usage, UsageStatus.PUBLIC)

        unit.update(UsageStatus.PRIVATE)
        self.assertEqual(unit.usage, UsageStatus.PUBLIC_AND_PRIVATE)

    def test_update_to_private_and_then_public(self):
        unit = UsageStatusTracker()

        unit.update(UsageStatus.PRIVATE)
        self.assertEqual(unit.usage, UsageStatus.PRIVATE)

        unit.update(UsageStatus.PUBLIC)
        self.assertEqual(unit.usage, UsageStatus.PUBLIC_AND_PRIVATE)

    def test_public_and_private_state_is_stable(self):
        unit = self.make_tracker_with_value(UsageStatus.PUBLIC_AND_PRIVATE)

        unit.update(UsageStatus.PUBLIC)
        self.assertEqual(unit.usage, UsageStatus.PUBLIC_AND_PRIVATE)

        unit.update(UsageStatus.PRIVATE)
        self.assertEqual(unit.usage, UsageStatus.PUBLIC_AND_PRIVATE)

        unit.update(UsageStatus.PUBLIC_AND_PRIVATE)
        self.assertEqual(unit.usage, UsageStatus.PUBLIC_AND_PRIVATE)

    def test_repr(self):
        unit_a = UsageStatusTracker()
        self.assertEqual(repr(unit_a), "NONE")

        unit_b = self.make_tracker_with_value(UsageStatus.PUBLIC)
        self.assertEqual(repr(unit_b), "PUBLIC")

        unit_c = self.make_tracker_with_value(UsageStatus.PRIVATE)
        self.assertEqual(repr(unit_c), "PRIVATE")

        unit_d = self.make_tracker_with_value(UsageStatus.PUBLIC_AND_PRIVATE)
        self.assertEqual(repr(unit_d), "PUBLIC_AND_PRIVATE")


class TestHeaderFile(unittest.TestCase):
    def test_repr(self):
        unit = HeaderFile("foo/bar.h")

        self.assertEqual(repr(unit), "HeaderFile(path='foo/bar.h', usage='NONE')")


class TestIncludePath(unittest.TestCase):
    def test_repr(self):
        unit = IncludePath("foo/bar.h")

        self.assertEqual(repr(unit), "IncludePath(path='foo/bar.h', usage='NONE')")


class TestCcTarget(unittest.TestCase):
    def test_repr(self):
        unit = CcTarget(name="//:foo", include_paths=[IncludePath("foo.h")], header_files=[HeaderFile("bar.h")])

        self.assertEqual(
            repr(unit),
            "CcTarget(name='//:foo',"
            " include_paths=[IncludePath(path='foo.h', usage='NONE')],"
            " header_files=[HeaderFile(path='bar.h', usage='NONE')])",
        )


class TestGetSystemUnderInspection(unittest.TestCase):
    def check_target(
        self, actual: CcTarget, expected_name: str, expected_paths: List[str], expected_files: List[str]
    ) -> None:
        self.assertEqual(actual.name, expected_name)

        self.assertEqual(len(actual.include_paths), len(expected_paths))
        for ip, expected_path in zip(actual.include_paths, expected_paths):
            self.assertEqual(ip.path, expected_path)
            self.assertEqual(ip.usage.usage, UsageStatus.NONE)

        self.assertEqual(len(actual.header_files), len(expected_files))
        for hf, expected_file in zip(actual.header_files, expected_files):
            self.assertEqual(hf.path, expected_file)
            self.assertEqual(hf.usage.usage, UsageStatus.NONE)

    def test_load_full_file(self):
        sui = get_system_under_inspection(Path("src/analyze_includes/test/data/headers_info_full.json"))

        self.assertEqual(len(sui.private_deps), 2)
        self.check_target(
            actual=sui.private_deps[0],
            expected_name="//private/dep:foo",
            expected_paths=["private/dep/foo_a.h", "private/dep/foo_b.h"],
            expected_files=["private/dep/foo_1.h", "private/dep/foo_2.h"],
        )
        self.check_target(
            actual=sui.private_deps[1],
            expected_name="//private/dep:bar",
            expected_paths=["private/dep/bar_a.h", "private/dep/bar_b.h"],
            expected_files=["private/dep/bar_1.h", "private/dep/bar_2.h"],
        )

        self.assertEqual(len(sui.public_deps), 2)
        self.check_target(
            actual=sui.public_deps[0],
            expected_name="//public/dep:foo",
            expected_paths=["public/dep/foo_a.h", "public/dep/foo_b.h"],
            expected_files=["public/dep/foo_1.h", "public/dep/foo_2.h"],
        )
        self.check_target(
            actual=sui.public_deps[1],
            expected_name="//public/dep:bar",
            expected_paths=["public/dep/bar_a.h", "public/dep/bar_b.h"],
            expected_files=["public/dep/bar_1.h", "public/dep/bar_2.h"],
        )

        self.assertEqual(sui.defines, ["SOME_DEFINE", "ANOTHER_DEFINE=42"])

        self.check_target(
            actual=sui.target_under_inspection,
            expected_name="//:baz",
            expected_paths=["self/a.h", "self/b.h"],
            expected_files=["self/header_1.h", "self/header_2.h"],
        )

    def test_load_empty_file(self):
        sui = get_system_under_inspection(Path("src/analyze_includes/test/data/headers_info_empty.json"))

        self.assertEqual(len(sui.private_deps), 0)
        self.assertEqual(len(sui.public_deps), 0)

        self.check_target(
            actual=sui.target_under_inspection,
            expected_name="//:foo",
            expected_paths=[],
            expected_files=[],
        )


if __name__ == "__main__":
    unittest.main()
