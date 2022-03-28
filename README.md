# Depend on what you use (DWYU)

DWYU is a Bazel aspect for C++ projects to make sure the headers your targets are using are aligned with the targets dependency list.
It applies the principals established by [Include What You Use](https://github.com/include-what-you-use/include-what-you-use)
to the dependencies of your `cc_*` targets.

The main features are:
* Finding include statements which are not available through a direct dependency, aka **preventing to rely on transitive dependencies**.
* Finding unused dependencies.
* Given one uses the latest experimental Bazel features, making sure one distinguishes properly between public and private dependencies for `cc_library`.
  For more details see [Ensure a proper split between public and private dependencies](#Ensure-a-proper-split-between-public-and-private-dependencies).

# Word of Warning

This project is still in a prototyping phase.
It has been made public to ease sharing with other developers for gathering feedback on the concept.
Do not expect stability of
* the project structure
* the feature set
* the tools chosen to implement DWYU

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

load("@depend_on_what_you_use//:dependencies.bzl", dwyu_public_dependencies = "public_dependencies")

dwyu_public_dependencies()
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

## Features

### Custom header ignore list

By default DWYU ignores all header from the standard library when comparing include statements to the dependencies.

You can exclude a custom set of header files by providing a config file in json format to the aspect.
An example for this and the correct format can be seen at [test/custom_config](../test/custom_config).

### Recursion

By default DWYU analyzes only the target it is being applied to.

You can activate recursive analysis, meaning the aspect analyzes recursively all dependencies of the target it is being
applied to. Activate this behavior via:
```
your_aspect = dwyu_aspect_factory(recursive = True)
```

This can be used to create a rule invoking DWYU on a target and all its dependencies as part of a normal build command.
Also it can be a convenience to analyze specific fraction of your stack without utilizing bazel (c)query.

Examples for this can be seen at [test/recursion](../test/recursion).

### Measure dependency utilization

If a library provides many headers but typically only a fraction of them are used at the call sites, this can be a hint
that the library should be split into smaller parts. DWYU allows you to find cases where a percentage less than
a provided threshold of headers from a dependency is used by a call site.

This feature is intended to analyze your stack and search for suboptimal dependencies. It is not recommended to enforce
unconditionally a minimum dependency header utilization on your whole stack. \
Using `include_prefix`, `strip_include_prefix` or `includes` on `cc_` targets tampers with the reliability of this measurement.
Those attributes make multiple include paths available for a single header file.
These, paths appear as multiple files to the DWYU implementation.
Consequently, the amount of headers provided by a dependency increases virtually and thus utilization drops.

Activate this behavior via:
```
your_aspect = dwyu_aspect_factory(min_utilization = [0..100])
```

Examples for this can be seen at [test/dependency_utilization](../test/dependency_utilization).

### Ensure a proper split between public and private dependencies

Starting with version 5.0.0 Bazel offers experimental features to distinguish between public (aka interface) and
private (aka implementation) dependencies for `cc_library`.
The private dependencies are not made available to users of the library to trim down dependency trees.

DWYU analyzes the usage of headers from the dependencies and can raise an error if a dependency is used only in
private files, but not put into the private dependency attribute.

#### Implementation_deps

**WARNING** \
`implementation_deps` is being removed again with Bazel 6.0.0.
DWYUs support for it may be removed at any point since it is of little value to support an experimental feature which
is available only in a single Bazel version.
See [Interface_deps](#Interface_deps) for the forward path, which is however as well only in experimental stage.

Bazel 5.0.0 introduces the experimental feature [`implementation_deps`](https://docs.bazel.build/versions/main/be/c-cpp.html#cc_library.implementation_deps)
for `cc_library`. In short, this enables you to specify dependencies which are only relevant for your `srcs` files and
are not made available to users of the library.

DWYU can report dependencies which are only used in private sources and should be moved from `deps` to `implementation_deps`.

Activate this behavior via:
```
your_aspect = dwyu_aspect_factory(use_implementation_deps = True)
```

Examples for this can be seen at [test/implementation_deps](../test/implementation_deps).

#### Interface_deps

This is not yet supported by DWYU.

https://github.com/bazelbuild/bazel/commit/56409448dfd7507f551f65283b4214020754c25c introduces `--experimental_cc_interface_deps`.
However an issue about potential problems with this new approach was raised: https://github.com/bazelbuild/bazel/issues/14950.
We will wait some time to make sure `interface_deps` really is the forward path before investing time into this.

## Supported Platforms

### Bazel

Minimum required Bazel version is **4.0.0**.
* Before 3.3.0 CcInfo compilation_context has a structure which is not supported by the aspect
* Before 4.0.0 the global json module is not available in Starlark


Maximum available Bazel version  is **6.0.0-pre.20220216.3**.
`implementation_deps` will be removed again in Bazel 6.0.0.

### Python

Requires Python 3. Code is only tested with Python 3.8, but should work with most 3.X versions.

## Operating system

DWYU is not designed for a specific platform.
Ubuntu 20.04 is however the only OS DWYU is currently being tested on.

## Known limitations

* If includes are added through a macro, this is invisible to DWYU.
* Defines are ignored.
  No matter if they are defined directly inside the header under inspection, headers from the dependencies or injected through the `defines = [...]` attribute of the `cc_` rules.
* Include statements utilizing `..` to go up the directory tree are not resolved.

# Project Roadmap

## Overview of current state

The focus until now has been to come up with a prototype for the idea behind DWYU and to be able to gather first user feedback.

[Test cases](test) have been established to make sure the concept works with a wide range of use cases and DWYU can evolve without introducing regressions.

The Bazel aspect implementation is for sure not yet ideal, but is considered it a solid starting point.

The Python implementation to analyze the include statements in C++ code is a minimal implementation with [several restrictions](#Known-limitations).
If it will be expanded or replaced is currently unclear.

# Contributing

See [Contributing](CONTRIBUTING.md).

# License

Copyright © 2022-present, [Martin Medler](https://github.com/martis42). \
This project licensed under the [MIT](https://opensource.org/licenses/MIT) license.
