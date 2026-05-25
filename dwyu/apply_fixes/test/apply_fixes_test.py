import argparse
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from python.runfiles import Runfiles

from dwyu.apply_fixes.apply_fixes import get_buildozer_binary, get_workspace


class TestGetBuildozerBinary(unittest.TestCase):
    def test_custom_binary_exists(self) -> None:
        runfiles = Runfiles.Create()
        buildozer = runfiles.Rlocation("depend_on_what_you_use/dwyu/apply_fixes/test/data/some_buildozer")

        result = get_buildozer_binary(Path(buildozer))

        self.assertEqual(result, str(buildozer))

    def test_custom_binary_does_not_exist(self) -> None:
        with self.assertLogs(level="FATAL") as captured_logs:
            result = get_buildozer_binary(Path("foo"))

        self.assertIsNone(result)
        self.assertEqual(
            captured_logs.output, ["CRITICAL:root:ERROR: The provided buildozer binary 'foo' does not exist."]
        )

    def test_bundled_binary_found(self) -> None:
        result = get_buildozer_binary(None)

        self.assertIsNotNone(result)
        self.assertTrue(result.endswith("buildozer_binary/buildozer.exe"))

    @patch("dwyu.apply_fixes.apply_fixes.Runfiles")
    def test_bundled_binary_not_found(self, mock_runfiles_cls: MagicMock) -> None:
        mock_runfiles = MagicMock()
        mock_runfiles.Rlocation.return_value = None
        mock_runfiles_cls.Create.return_value = mock_runfiles

        with self.assertLogs(level="FATAL") as captured_logs:
            result = get_buildozer_binary(None)

        self.assertIsNone(result)
        self.assertEqual(len(captured_logs.output), 1)
        self.assertTrue(
            captured_logs.output[0].startswith("CRITICAL:root:ERROR: Failed to discover the bundled buildozer binary.")
        )


class TestGetWorkspace(unittest.TestCase):
    def test_workspace_from_args(self) -> None:
        args = argparse.Namespace(workspace=Path("/explicit/workspace"))

        result = get_workspace(args)

        self.assertEqual(result, Path("/explicit/workspace"))

    @patch("dwyu.apply_fixes.apply_fixes.environ", {"BUILD_WORKSPACE_DIRECTORY": "/env/workspace"})
    def test_workspace_from_env_var(self) -> None:
        args = argparse.Namespace(workspace=None)

        result = get_workspace(args)

        self.assertEqual(result, Path("/env/workspace"))

    @patch("dwyu.apply_fixes.apply_fixes.environ", {})
    def test_no_workspace_available(self) -> None:
        args = argparse.Namespace(workspace=None)

        result = get_workspace(args)

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
