- [Depend on what you use (DWYU)](#depend-on-what-you-use-dwyu)
- [Getting started](#getting-started)
  - [Get a release](#get-a-release)
  - [Get a specific commit](#get-a-specific-commit)
  - [Use DWYU](#use-dwyu)
- [Features](#features)
  - [Custom header ignore list](#custom-header-ignore-list)
  - [Recursion](#recursion)
  - [Implementation\_deps](#implementation_deps)
  - [Known limitations](#known-limitations)
  - [Applying automatic fixes](#applying-automatic-fixes)
- [Supported Platforms](#supported-platforms)
- [Alternatives to DWYU](#alternatives-to-dwyu)
- [Versioning](#versioning)
- [Contributing](#contributing)
- [License](#license)

# Depend on what you use (DWYU)

DWYU is a Bazel aspect for C++ projects making sure the headers your Bazel targets are using are aligned with their dependency lists.

DWYUs enforces the design principle:<br/>
**A `cc_*` target X shall depend directly on the targets providing the header files which are included in the source code of X.**

The main features are:
- Finding include statements which are not available through a direct dependency, aka **preventing to rely on transitive dependencies for includes**.
- Finding unused dependencies.
- Given one uses the latest experimental Bazel features, making sure one distinguishes properly between public and
  private dependencies for `cc_library`. For more details see
  [Ensure a proper split between public and private dependencies](#Ensure-a-proper-split-between-public-and-private-dependencies).

More information about the idea behind DWYU and the implementation of the project is available in [the docs](docs/).

# Getting started

## Get a release

Choose a release from the [release page](https://github.com/martis42/depend_on_what_you_use/releases) and follow the instructions.

## Get a specific commit

Put the following into your `WORKSPACE` file to use a specific DWYU commit:
```python
load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

dwyu_version = "<git_commit_hash>"
http_archive(
    name = "depend_on_what_you_use",
    sha256 = "<archive_checksum>",  # optional
    strip_prefix = "depend_on_what_you_use-{}".format(dwyu_version),
    url = "https://github.com/martis42/depend_on_what_you_use/archive/{}.tar.gz".format(dwyu_version),
)

load("@depend_on_what_you_use//:dependencies.bzl", dwyu_dependencies = "public_dependencies")
dwyu_dependencies()
```

## Use DWYU

### Configure the aspect

Configure an aspect with the desired behavior.
The features which can be configured trough the the aspect factory attributes are documented at [Features](#features).
Put the following inside a `aspect.bzl` file (file name is exemplary):
```python
load("@depend_on_what_you_use//:defs.bzl", "dwyu_aspect_factory")

# Provide no arguments for the default behavior
# Or set a custom value for the various attributes
your_dwyu_aspect = dwyu_aspect_factory()
```

### Use the aspect

Invoke the aspect through the command line on a target:<br/>
`bazel build <target_pattern> --aspects=//:aspect.bzl%your_dwyu_aspect --output_groups=cc_dwyu_output`

If no problem is found, the command will exit with `INFO: Build completed successfully`.<br/>
If a problem is detected, the build command will fail with an error and a description of the problem will be printed in
the terminal. For example:
```
================================================================================
DWYU analyzing: '<analyzed_target>'

Result: Failure

Unused dependencies in 'deps' (none of their headers are referenced):
  Dependency='//some/target/with_an_unused:dependency'
===============================================================================
```

### Create a rule invoking the aspect.

You can invoke the aspect from within a rule. This can be useful to make the execution part of a bazel build (e.g.
`bazel build //...`) without having to manually execute the longish aspect build command.

The Bazel documentation for invoking an aspect from within a rule can be found [here](https://bazel.build/rules/aspects#invoking_the_aspect_from_a_rule).
A concrete example for doing so for the DWYU aspect can be found in [a rule in the recursion test cases](test/aspect/recursion/rule.bzl).

# Features

## Custom header ignore list

By default DWYU ignores all header from the standard library when comparing include statements to the dependencies.
This list of headers can be seen in [std_header.py](src/analyze_includes/std_header.py).

You can exclude a custom set of header files by providing a config file in json format to the aspect:
```python
your_aspect = dwyu_aspect_factory(config = "//<your_config_file>.json")
```

The config file can contain these fields which should be lists of strings. All fields are optional:

| Field                        | Description                                                                                                                                                                                                                      |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ignore_include_paths`       | List of include paths which are ignored by the analysis. Setting this **disables ignoring the standard library include paths**.                                                                                                  |
| `extra_ignore_include_paths` | List of include paths which are ignored by the analysis. If `ignore_include_paths` is specified as well, both list are combined. If `ignore_include_paths` is not set, the default list of standard library headers is extended. |
| `ignore_include_patterns`    | List of patterns for include paths which are ignored by the analysis. Patterns have to be compatible to Python [re](https://docs.python.org/3/library/re.html#regular-expression-syntax).                                        |


Examples and the correct format can be seen at the [custom config test cases](test/aspect/custom_config).

## Recursion

By default DWYU analyzes only the target it is being applied to.

You can also activate recursive analysis. Meaning the aspect analyzes recursively all dependencies of the target it is
being applied to:
```python
your_aspect = dwyu_aspect_factory(recursive = True)
```

This can be used to create a rule invoking DWYU on a target and all its dependencies as part of a normal build command.
Also it can be a convenience to analyze specific fraction of your stack without utilizing bazel (c)query.

Examples for this can be seen at the [recursion test cases](test/aspect/recursion).

## Implementation_deps

Starting with version 5.0.0 Bazel offers experimental feature [`implementation_deps`](https://docs.bazel.build/versions/5.0.0/be/c-cpp.html#cc_library.implementation_deps)
to distinguish between public (aka interface) and private (aka implementation) dependencies for `cc_library`.
Headers from the private dependencies are not made available to users of the library to trim down dependency trees.

DWYU analyzes the usage of headers from the dependencies and can raise an error if a dependency is used only in
private files, but not put into the private dependency attribute. Meaning, it can find dependencies which should be
move from `deps` to `implementation_deps`.

Activate this behavior via:
```python
your_aspect = dwyu_aspect_factory(use_implementation_deps = True)
```

Examples for this can be seen at the [implementation_deps test cases](test/aspect/implementation_deps).

## Known limitations

- If includes are added through a macro, this is invisible to DWYU.
- Defines are ignored.
  No matter if they are defined directly inside the header under inspection, headers from the dependencies or injected
  through the `defines = [...]` attribute of the `cc_` rules.
- Include statements utilizing `..` to go up the directory tree are not resolved.

## Applying automatic fixes

DWYU offers a tool to automatically fix detected problems.

The workflow is the following:
1. Execute DWYU on your workspace. DWYU will create report files containing information about discovered problems for
   each analyzed target in the Bazel output directory.
2. Execute `bazel run @depend_on_what_you_use//:apply_fixes`. The tool discovers the report files generated in the
   previous step and gathers the problems for which a fix is available. Then [buildozer](https://github.com/bazelbuild/buildtools/blob/master/buildozer/README.md)
   is utilized to adapt the BUILDS files in your workspace.

If the `apply_fixes` tool is not able to discover the report files, this can be caused by the `bazel-bin` convenience
symlink at the workspace root not existing or not pointing to the output directory which was used by to generate the
report files.
The `apply_fixes` tool offers options to control how the output directory is discovered.<br/>
Execute `bazel run @depend_on_what_you_use//:apply_fixes -- --help` to discover the whole CLI interface of the tool.

There are limitations on what can be automatically fixed due to constrraints of `buildozer`. For more details
see the doc string of the [apply fixes main function](src/apply_fixes/main.py).

# Supported Platforms

| Platform         | Constraints                                                                                      |
| ---------------- | ------------------------------------------------------------------------------------------------ |
| Operating system | No constraints. However, Ubuntu 20.04 is currently the only OS used for development and testing. |
| Python           | Minimum version is 3.6. Tests are currently running based on Python 3.8.                         |
| Bazel            | Minimum version is 4.0.0. Multiple versions are tested.                                          |
| Buildozer        | No known limitations. Tests have been performed with 5.0.1.                                      |

# Alternatives to DWYU

If you are mostly interested in making sure no headers from transitive dependecies are used by your C++ targets, you
might want to look into the `layering_check` feature.
It causes the compilation to fail on using headers from transitive dependencies.<br/>
At the time of writing this, I could not find detailed documentation about this feature.
It was introduced in [this PR](https://github.com/bazelbuild/bazel/pull/11440) and is mentioned in the [unix_cc_toolchain_config.bzl](https://github.com/bazelbuild/bazel/blob/master/tools/cpp/unix_cc_toolchain_config.bzl).<br/>
As far as I can tell this feature is only available with the clang compiler and while using modules.

# Versioning

This project uses [semantic versioning](https://semver.org/spec/v2.0.0.html).
Please be aware that the project is still in an early phase and until version 1.0.0 has been reached all releases
can contain breaking changes.

# Contributing

See [Contributing](CONTRIBUTING.md).

# License

Copyright © 2022-present, [Martin Medler](https://github.com/martis42). \
This project licensed under the [MIT](https://opensource.org/licenses/MIT) license.
