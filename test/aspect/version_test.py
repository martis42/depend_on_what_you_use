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

    def test_only_rolling_is_compatible_to_min_version_rolling(self) -> None:
        self.assertFalse(CompatibleVersions(minimum="rolling").is_compatible_to("999.999.999"))
        self.assertTrue(CompatibleVersions(minimum="rolling").is_compatible_to("rolling"))

    def test_max_version_rolling_is_compatible_to_all_except_rolling(self) -> None:
        self.assertTrue(CompatibleVersions(before="rolling").is_compatible_to("999.999.999"))
        self.assertFalse(CompatibleVersions(before="rolling").is_compatible_to("rolling"))


if __name__ == "__main__":
    unittest.main()
