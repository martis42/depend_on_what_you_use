# Test Strategy

## General

Formatting and linting as well as unit tests are executed on the main development platform for this project, which is Linux.
Those tests and checks run with the Bazel version defined in `.bazelversion`.

Whenever we test with multiple Bazel versions, we test the minimum required Bazel version of this project and the latest release of each supported Bazel major version.

## Aspect

We aim at executing Integration tests with multiple Bazel versions on all supported platforms.
On Windows we can only test a single Bazel version due to Bazel being significantly slower on Windows.

## Applying fixes

We execute the integration tests on all supported platforms with a single Bazel version.
Since, those tests are quite slow, running them with multiple Bazel versions would be too expensive.
