This directory contains the acceptance tests.
They are executed with various supported Bazel versions.
[bazelisk](https://github.com/bazelbuild/bazelisk) has to be available on `PATH`.

The test cases and their expected behavior are defined in [execute_tests.py](execute_tests.py).

Execute all tests with various Bazel versions: \
`./execute_tests.py`

You can execute specific test cases or use specific Bazel versions. For details see the help: \
`./execute_tests.py --help`
