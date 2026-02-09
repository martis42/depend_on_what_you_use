This directory contains the integration tests for the automatic fixing tool.

Each `test_*.py` file represents a test case. The `execute_test.py` script is the entry point for the test suite.

The core test logic is:

1. Execute DWYU to detect a problem
1. Execute `//:apply_fixes` to fix the problem in the example `BUILD` file
1. Check if the expected fix happened
1. Revert changes to the example `BUILD` file

The actual code examples are in a dedicated `workspace` sub directory to ease reverting changes done to them by buildozer.
