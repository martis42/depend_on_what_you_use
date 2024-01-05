import unittest

from version import CompatibleVersions


class TestIsCompatibleVersion(unittest.TestCase):
    def test_no_limits(self) -> None:
        self.assertTrue(CompatibleVersions().is_compatible_to("1.0.0"))

    def test_above_min_version(self) -> None:
        self.assertTrue(CompatibleVersions(minimum="0.9.9").is_compatible_to("1.0.0"))

    def test_exactly_min_version(self) -> None:
        self.assertTrue(CompatibleVersions(minimum="1.2.0").is_compatible_to("1.2.0"))

    def test_below_min_version(self) -> None:
        self.assertFalse(CompatibleVersions(minimum="1.1.9").is_compatible_to("1.0.0"))

    def test_below_max_version(self) -> None:
        self.assertTrue(CompatibleVersions(before="1.1.0").is_compatible_to("1.0.0"))

    def test_exactly_max_version(self) -> None:
        self.assertFalse(CompatibleVersions(before="1.2.0").is_compatible_to("1.2.0"))

    def test_above_max_version(self) -> None:
        self.assertFalse(CompatibleVersions(before="0.9.0").is_compatible_to("1.0.0"))

    def test_inside_interval(self) -> None:
        self.assertTrue(CompatibleVersions(minimum="0.9.0", before="1.1.0").is_compatible_to("1.0.0"))


if __name__ == "__main__":
    unittest.main()
