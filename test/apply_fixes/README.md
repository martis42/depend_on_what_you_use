This directory contains the integration tests for the automatic fixing tool.

Each `test_*.py` file represents a test case. The `execute_test.py` is the entry point for the test suite.

For each test case the workspace template is copied into a temporary directory in which then DWYU is executed to detect
a problem. Afterwards, the `//:apply_fixes` tool is executed and the adapted `BUILD` files are analyzed to check if the
expected change happened.<br/>
This approach based on a temporary workspace is chosen to make sure cleaning up the test side effects is not
messing with the source code.
