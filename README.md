# Depend on what you use (DWYU)

DWYU is a Bazel aspect for C++ projects making sure the headers your Bazel targets are using are aligned with their dependency lists.

DWYUs enforces the design principle: \
**A `cc_*` target X shall depend directly on the targets providing the header files which are included in the source code of X.**

The main features are:
* Finding include statements which are not available through a direct dependency, aka **preventing to rely on transitive dependencies for includes**.
* Finding unused dependencies.
* Given one uses the latest experimental Bazel features, making sure one distinguishes properly between public and private dependencies for `cc_library`.
  For more details see [Ensure a proper split between public and private dependencies](#Ensure-a-proper-split-between-public-and-private-dependencies).

For more information about the DWYU design principle see [the docs](docs/design_principle.md).

# Getting started

## Get a release

Choose a release from the [release page](https://github.com/martis42/depend_on_what_you_use/releases) and follow the instructions.

## Get a specific commit

Put the following into your `WORKSPACE` file:
```sh
load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

dwyu_version = "<git_commit_sha>"

http_archive(
    name = "depend_on_what_you_use",
    sha256 = "<archive_checksum>",
    strip_prefix = "depend_on_what_you_use-{}".format(dwyu_version),
    url = "https://github.com/martis42/depend_on_what_you_use/archive/{}.zip".format(dwyu_version),
)

load("@depend_on_what_you_use//:dependencies.bzl", dwyu_dependencies = "public_dependencies")

dwyu_dependencies()
```

## Use DWYU

### Configure the aspect

Configure an aspect with the desired behavior.
The features which can be configured trough the the aspect factory attributes are documented at [Features](#features).
Put the following inside a `aspect.bzl` file (file name is exemplary):
```sh
load("@depend_on_what_you_use//:defs.bzl", "dwyu_aspect_factory")

# Provide no arguments for the default behavior
# Or set a custom value for the various attributes
your_dywu_aspect = dwyu_aspect_factory()
```

### Use the aspect

Invoke the aspect through the command line on a target: \
`bazel build <target_pattern> --aspects=//:aspect.bzl%your_dywu_aspect --output_groups=cc_dwyu_output`

If no problem is found, the command will exit with `INFO: Build completed successfully`. \
If a problem is detected, the build command will fail with an error and a description of the problem will be printed in the terminal.
For example:
```
================================================================================
DWYU analyzing: '<analyzed_target>'

Result: Failure

Unused dependencies (none of their headers are referenced):
  Dependency='//some/target/with_an_unused:dependency'
===============================================================================
```

### Create a rule invoking the aspect.

You can invoke the aspect from within a rule.
This can be useful to make the execution part of a bazel build (e.g. `bazel build //...`) without having to execute the longish manual aspect build command.

The Bazel documentation for invoking an aspect from within a rule can be found [here](https://bazel.build/rules/aspects#invoking_the_aspect_from_a_rule).
A concrete example for doing so for a DWYU aspect can be [found in the recursion test cases](test/recursion/rule.bzl).

# Features

## Custom header ignore list

By default DWYU ignores all header from the standard library when comparing include statements to the dependencies.

You can exclude a custom set of header files by providing a config file in json format to the aspect:
```
your_aspect = dwyu_aspect_factory(config = "//<your_config_file>.json")
```

Examples and the correct format can be seen at [test/custom_config](test/custom_config).

## Recursion

By default DWYU analyzes only the target it is being applied to.

You can also activate recursive analysis. Meaning the aspect analyzes recursively all dependencies of the target it is being
applied to:
```
your_aspect = dwyu_aspect_factory(recursive = True)
```

This can be used to create a rule invoking DWYU on a target and all its dependencies as part of a normal build command.
Also it can be a convenience to analyze specific fraction of your stack without utilizing bazel (c)query.

Examples for this can be seen at [test/recursion](test/recursion).

## Ensure a proper split between public and private dependencies

Starting with version 5.0.0 Bazel offers experimental features to distinguish between public (aka interface) and
private (aka implementation) dependencies for `cc_library`.
The private dependencies are not made available to users of the library to trim down dependency trees.

DWYU analyzes the usage of headers from the dependencies and can raise an error if a dependency is used only in
private files, but not put into the private dependency attribute.

### Implementation_deps

:warning: **`implementation_deps` is being removed again with Bazel 6.0.0**.
See [Interface_deps](#Interface_deps) for the forward path, which is however as well only in experimental stage.

Bazel 5.0.0 introduces the experimental feature [`implementation_deps`](https://docs.bazel.build/versions/main/be/c-cpp.html#cc_library.implementation_deps)
for `cc_library`. In short, this enables you to specify dependencies which are only relevant for your `srcs` files and
are not made available to users of the library.

DWYU can report dependencies which are only used in private sources and should be moved from `deps` to `implementation_deps`.

Activate this behavior via:
```
your_aspect = dwyu_aspect_factory(use_implementation_deps = True)
```

Examples for this can be seen at [test/implementation_deps](test/implementation_deps).

### Interface_deps

This is not yet supported by DWYU.

https://github.com/bazelbuild/bazel/commit/56409448dfd7507f551f65283b4214020754c25c introduces `--experimental_cc_interface_deps`.
However an issue about potential problems with this new approach was raised: https://github.com/bazelbuild/bazel/issues/14950.
We will wait some time to make sure `interface_deps` really is the forward path before investing time into this.

## Known limitations

* If includes are added through a macro, this is invisible to DWYU.
* Defines are ignored.
  No matter if they are defined directly inside the header under inspection, headers from the dependencies or injected through the `defines = [...]` attribute of the `cc_` rules.
* Include statements utilizing `..` to go up the directory tree are not resolved.

# Supported Platforms

## Operating system

DWYU is not designed for a specific platform.
Ubuntu 20.04 is however the only OS DWYU is currently being tested on.

## Bazel

Minimum required Bazel version is **4.0.0**.
* Before 3.3.0 CcInfo compilation_context has a structure which is not supported by the aspect
* Before 4.0.0 the global json module is not available in Starlark

## Python

Requires Python 3. Code is only tested with Python 3.8, but should work with most 3.X versions.

# Contributing

See [Contributing](CONTRIBUTING.md).

# License

Copyright © 2022-present, [Martin Medler](https://github.com/martis42). \
This project licensed under the [MIT](https://opensource.org/licenses/MIT) license.
