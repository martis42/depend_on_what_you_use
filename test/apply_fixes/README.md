This directory contains the acceptance tests for the automatic fixing tool.

Each sub directory represents a test case. The content of each sub directory is copied into a temporary directory
in which then DWYU is executed to detect a problem. Afterwards, the `//:apply_fixes` tool is executed and the adapted
`BUILD` files are analyzed to check if the expected change happened. Finally, the temporary directory is cleaned up.<br/>
This approach based on a temporary workspace is chosen to make sure cleaning up the test side effects is not
messing with the source code.
