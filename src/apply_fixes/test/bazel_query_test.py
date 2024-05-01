import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.apply_fixes.bazel_query import BazelQuery


class TestBazelQuery(unittest.TestCase):
    @patch("src.apply_fixes.bazel_query.execute_and_capture", return_value=None)
    def test_execute_simple_query(self, execute_and_capture_mock: MagicMock) -> None:
        unit = BazelQuery(workspace=Path("foo/bar"), use_cquery=False, query_args=[], startup_args=[])
        unit.execute(query="deps(//foo:bar)", args=[])
        execute_and_capture_mock.assert_called_once_with(cmd=["bazel", "query", "deps(//foo:bar)"], cwd=Path("foo/bar"))

    @patch("src.apply_fixes.bazel_query.execute_and_capture", return_value=None)
    def test_execute_query_with_args(self, execute_and_capture_mock: MagicMock) -> None:
        unit = BazelQuery(
            workspace=Path("foo/bar"),
            use_cquery=False,
            query_args=["--foo", "--tick=tock"],
            startup_args=["--bar", "--fizz=buzz"],
        )
        unit.execute(query="deps(//foo:bar)", args=[])
        execute_and_capture_mock.assert_called_once_with(
            cmd=["bazel", "--bar", "--fizz=buzz", "query", "--foo", "--tick=tock", "deps(//foo:bar)"],
            cwd=Path("foo/bar"),
        )

    @patch("src.apply_fixes.bazel_query.execute_and_capture", return_value=None)
    def test_execute_cquery(self, execute_and_capture_mock: MagicMock) -> None:
        unit = BazelQuery(workspace=Path("foo/bar"), use_cquery=True, query_args=[], startup_args=[])
        unit.execute(query="deps(//foo:bar)", args=[])
        execute_and_capture_mock.assert_called_once_with(
            cmd=["bazel", "cquery", "deps(//foo:bar)"], cwd=Path("foo/bar")
        )

    def test_uses_cquery_property_is_true(self) -> None:
        unit = BazelQuery(workspace=Path("foo/bar"), use_cquery=True, query_args=[], startup_args=[])
        self.assertTrue(unit.uses_cquery)

    def test_uses_cquery_property_is_false(self) -> None:
        unit = BazelQuery(workspace=Path("foo/bar"), use_cquery=False, query_args=[], startup_args=[])
        self.assertFalse(unit.uses_cquery)


if __name__ == "__main__":
    unittest.main()
