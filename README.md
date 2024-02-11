[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

- [Depend on what you use (DWYU)](#depend-on-what-you-use-dwyu)
- [Getting started](#getting-started)
  - [Get a release](#get-a-release)
  - [Get a specific commit](#get-a-specific-commit)
  - [Use DWYU](#use-dwyu)
- [Configuring DWYU](#configuring-dwyu)
  - [Custom header ignore list](#custom-header-ignore-list)
  - [Skipping Targets](#skipping-targets)
  - [Recursion](#recursion)
  - [Implementation_deps](#Implementation_deps)
  - [Target mapping](#target-mapping)
  - [Verbosity](#verbosity)
- [Applying automatic fixes](#applying-automatic-fixes)
- [Assumptions of use](#assumptions-of-use)
- [Supported Platforms](#supported-platforms)
- [Alternatives to DWYU](#alternatives-to-dwyu)
- [Versioning](#versioning)
- [Contributing](#contributing)
- [License](#license)

# Depend on what you use (DWYU)

DWYU is a Bazel aspect for C++ projects making sure the headers your Bazel targets are using are aligned with their dependency lists.

DWYUs enforces the design principle:<br>
**A `cc_*` target _X_ shall depend directly on the targets providing the header files which are included in the source code of _X_.**

The main features are:

- Finding include statements which are not available through a direct dependency, aka **preventing to rely on transitive dependencies for includes**.
- Finding unused dependencies.
- Given one uses [`implementation_deps`](https://bazel.build/reference/be/c-cpp#cc_library.implementation_deps), making sure one distinguishes properly between public and private dependencies for `cc_library` targets.
  For more details see [features chapter Implementation_deps](#Implementation_deps).

More information about the idea behind DWYU and the implementation of the project is available in [the docs](docs).

# Getting started

## Get a release

Choose a release from the [release page](https://github.com/martis42/depend_on_what_you_use/releases) and follow the instructions.

## Get a specific commit

### bzlmod (recommended)

Put the following into your `MODULE.bazel` file

```starlark
bazel_dep(name = "depend_on_what_you_use", version = "0.0.0")
git_override(
    module_name = "depend_on_what_you_use",
    commit = <commit_you_are_interested_in>,
    remote = "https://github.com/martis42/depend_on_what_you_use",
)
```

### legacy approach

Put the following into your `WORKSPACE` file to use a specific DWYU commit

```starlark
load("@bazel_tools//tools/build_defs/repo:git.bzl", "git_repository")
git_repository(
    name = "depend_on_what_you_use",
    commit = <commit_you_are_interested_in>,
    remote = "https://github.com/martis42/depend_on_what_you_use",
)

load("@depend_on_what_you_use//:setup_step_1.bzl", dwyu_setup_step_1 = "setup_step_1")
dwyu_setup_step_1()

load("@depend_on_what_you_use//:setup_step_2.bzl", dwyu_setup_step_2 = "setup_step_2")
dwyu_setup_step_2()
```

## Use DWYU

### Configure the aspect

The features which can be configured through the aspect factory attributes are documented at [Configuring DWYU](#configuring-dwyu).
Put the following inside a `.bzl` file:

```starlark
load("@depend_on_what_you_use//:defs.bzl", "dwyu_aspect_factory")

# Provide no arguments for the default behavior
# Or set a custom value for the various attributes
your_dwyu_aspect = dwyu_aspect_factory()
```

### Use the aspect

Invoke the aspect through the command line on a target:<br>
`bazel build <target_pattern> --aspects=//:aspect.bzl%your_dwyu_aspect --output_groups=dwyu`

If no problem is found, the command will exit with `INFO: Build completed successfully`.<br>
If a problem is detected, the build command will fail with an error and a description of the problem will be printed in the terminal. For example:

```
================================================================================
DWYU analyzing: '<analyzed_target>'

Result: Failure

Unused dependencies in 'deps' (none of their headers are referenced):
  Dependency='//some/target/with_an_unused:dependency'
===============================================================================
```

### Create a rule invoking the aspect

You can invoke the aspect from within a rule.
This can be useful to make the execution part of a bazel build without having to manually execute the longish aspect build command.

The Bazel documentation for invoking an aspect from within a rule can be found [here](https://bazel.build/rules/aspects#invoking_the_aspect_from_a_rule).

This is demonstrated in the [rule_using_dwyu example](/examples/rule_using_dwyu).

# Configuring DWYU

## Custom header ignore list

By default, DWYU ignores all header from the standard library when comparing include statements to the dependencies.
This list of headers can be seen in [std_header.py](src/analyze_includes/std_header.py).

You can exclude a custom set of header files by providing a config file in json format to the aspect:

```starlark
your_aspect = dwyu_aspect_factory(ignored_includes = "//<your_config_file>.json")
```

The config file can contain these fields which should be lists of strings.
All fields are optional:

| Field                        | Description                                                                                                                                                                                                                                                                                                   |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ignore_include_paths`       | List of include paths which are ignored by the analysis. Setting this **disables ignoring the standard library include paths**.                                                                                                                                                                               |
| `extra_ignore_include_paths` | List of include paths which are ignored by the analysis. If `ignore_include_paths` is specified as well, both list are combined. If `ignore_include_paths` is not set, the default list of standard library headers is extended.                                                                              |
| `ignore_include_patterns`    | List of patterns for include paths which are ignored by the analysis. Patterns have to be compatible to Python [regex syntax](https://docs.python.org/3/library/re.html#regular-expression-syntax). The [match](https://docs.python.org/3/library/re.html#re.match) function is used to process the patterns. |

This is demonstrated in the [ignoring_includes example](/examples/ignoring_includes).

## Skipping targets

If you want the DWYU aspect to skip certain targets and negative target patterns are not an option you can do so by setting the `no-dwyu` tag on those.
You can also configure the aspect to skip targets based on a custom list of tags:

```starlark
your_aspect = dwyu_aspect_factory(skipped_tags = ["tag1_marking_skipping", "tag2_marking_skipping"])
```

This is demonstrated in the [skipping_targets example](/examples/skipping_targets).

## Recursion

By default, DWYU analyzes only the target it is being applied to.

You can also activate recursive analysis.
Meaning the aspect analyzes recursively all dependencies of the target it is being applied to:

```starlark
your_aspect = dwyu_aspect_factory(recursive = True)
```

This is demonstrated in the [recursion example](/examples/recursion).

## Implementation_deps

Bazel offers the experimental feature [`implementation_deps`](https://bazel.build/reference/be/c-cpp#cc_library.implementation_deps) to distinguish between public (aka interface) and private (aka implementation) dependencies for `cc_library`.
Headers from the private dependencies are not made available to users of the library.

DWYU analyzes the usage of headers from the dependencies and can raise an error if a dependency is used only in private files, but not put into the private dependency attribute.
Meaning, it can find dependencies which should be moved from `deps` to `implementation_deps`.

Activate this behavior via:

```starlark
your_aspect = dwyu_aspect_factory(use_implementation_deps = True)
```

Usage of this can be seen in the [basic example](examples/basic_usage).

## Target mapping

Sometimes users don't want to follow the DWYU rules for all targets or have to work with external dependencies not following the DWYU principles.
For such cases DWYU allows creating a mapping which for a chosen target makes more headers available as the target actually provides.
In other words, one can combine virtually multiple targets for the DWYU analysis.
Doing so allows using headers from transitive dependencies without DWYU raising an error for select cases.

Such a mapping is created with the [dwyu_make_cc_info_mapping](src/cc_info_mapping/cc_info_mapping.bzl) rule.
This offers multiple ways of mapping targets:

1. Explicitly providing a list of targets which are mapped into a single target.
1. Specifying that all direct dependencies of a given target are mapped into the target.
1. Specifying that all transitive dependencies of a given target are mapped into the target.

Activate this behavior via:

```starlark
your_aspect = dwyu_aspect_factory(target_mapping = "<mapping_target_created_by_the_user>")
```

This is demonstrated in the [target_mapping example](/examples/target_mapping).

## Verbosity

One can configure the DWYU aspect to print debugging information.

Activate this behavior via:

```starlark
your_aspect = dwyu_aspect_factory(verbose = True)
```

# Applying automatic fixes

> \[!WARNING\]
> Please note that **the tool cannot guarantee that your build is not being broken** by the changes.
> Always make sure your project is still valid after the changes and review the performed changes.

DWYU offers a tool to automatically fix some detected problems.
The workflow is the following:

1. Execute DWYU on your workspace.
   DWYU will create report files containing information about discovered problems in the Bazel output directory for each analyzed target.
1. Execute `bazel run @depend_on_what_you_use//:apply_fixes -- <your_options>`.
   The tool discovers the report files generated in the previous step and gathers the problems for which a fix is available.
   Then, [buildozer](https://github.com/bazelbuild/buildtools/blob/master/buildozer/README.md) is utilized to adapt the BUILD files in your workspace.

The `apply_fixes` tool requires you to explicitly choose which kind or errors you want to be fixed.
You can see the full command line interface and more information about the script behavior and limitations by executing:<br>
`bazel run @depend_on_what_you_use//:apply_fixes -- --help`

If the `apply_fixes` tool is not able to discover the report files, this can be caused by the `bazel-bin` convenience symlink at the workspace root not existing or not pointing to the output directory which was used by to generate the report files.
The tool offers options to control how the output directory is discovered.

Unfortunately, the tool cannot promise perfect results due to various constraints:

- If alias targets are involved, this cannot be processed properly.
  Alias targets are resolved to their actual target before the DWYU aspect is running.
  Thus, the DWYU report file contains the actual targets in its report and buildozer is not able to modify the BUILD files containing the alias name.
- Buildozer is working on the plain BUILD files as a user would see them in the editor.
  Meaning without alias resolution or macro expansion.
  Consequently, buildozer cannot work on targets which are generated inside a macro or whose name is constructed.
- Adding missing direct dependencies is based on a heuristic and not guaranteed to find the correct dependency.
- If you execute DWYU only on some targets and not the complete build tree, this can break the overall build.
  For example dependency _X_ in library _A_ is unused and would be removed.
  But a downstream user of library _A_ might transitively depend on _X_.
  Removing the unused dependency will break the build as the downstream dependency no longer finds dependency _X_.

# Assumptions of use

##### The code has to be compilable

DWYU is not performing a compilation.
It works by statically analyzing the source code and build tree.
However, non compiling code can contain errors infringing the assumptions DWYU is based on.
For example, including header files which do not exist at the expected path.

##### Include paths have to be unambiguous

There shall not be multiple header files in the dependency tree of a target matching an include statement.
Even if analysing the code works initially, it might break at any time if the ordering of paths in the analysis changes.

# Supported Platforms

### Aspect

| Platform         | Constraints                                                                              |
| ---------------- | ---------------------------------------------------------------------------------------- |
| Operating system | No constraints by design. Tests are based on Ubuntu 22.04.                               |
| Python           | Minimum version is 3.8. All newer major versions until 3.12 are tested.                  |
| Bazel            | Minimum version is 5.4.0. Multiple newer versions are tested including rolling releases. |

### Applying fixes

| Platform         | Constraints                                                |
| ---------------- | ---------------------------------------------------------- |
| Operating system | No constraints by design. Tests are based on Ubuntu 22.04. |
| Python           | Minimum version is 3.8. Tests are based on Python 3.8.     |
| Bazel            | No constraints by design. Tests are based on 7.0.0.        |
| Buildozer        | No known limitations. Tests are based on 6.4.0.            |

# Alternatives to DWYU

## Layering check

To make sure no headers from transitive dependencies or private headers from dependencies are used you can use [Layering check with Clang](https://maskray.me/blog/2022-09-25-layering-check-with-clang) which is natively supported by Bazel.
The main benefit of this approach is it being directly integrated into Bazel without need of further tooling like DWYU.

Still, there are reasons to use DWYU instead of or in addition to layering_check:

- DWYU does not require a compiler, it works purely by text parsing.
  The only requirement towards your platform is the availability of a Python interpreter.
- DWYU is able to analyze header only libraries.
- DWYU detects unused dependencies.
- DWYU allows optimizing [implementation_deps](#implementation_deps).
- DWYU offers automatic fixes for detected issues.

## Gazelle

[Gazelle](https://github.com/bazelbuild/bazel-gazelle) is a tool automatically creating `BUILD` files for your code.
It seems there is no public and established C++ extension for gazelle.

Still, if one agrees with the best practices enforced by DWYU but cannot use it, investing time into a gazelle C++ extension might be worth it.
Automatically generating correct BUILD files based on your source code is a more efficient approach compared to having to manually execute DWYU regularly to make sure no error was introduced.

# Versioning

This project uses [semantic versioning](https://semver.org/spec/v2.0.0.html).
Please be aware that the project is still in an early phase and until version 1.0.0 has been reached all releases can contain breaking changes.

**The following things can always break** and do not promise stability with respect to the semantic versioning:

- The report files DWYU generates to facilitate running automatic fixes are considered an implementation detail.
  Changing their content is not considered a breaking change.
- How to include DWYU in your project git commit might change at any time.

# Contributing

See [Contributing](CONTRIBUTING.md).

# License

Copyright © 2022-present, [Martin Medler](https://github.com/martis42). <br>
This project licensed under the [MIT](https://opensource.org/licenses/MIT) license.

This projects references several other projects which each have individual licenses.
See the content of [third_party](third_party) for all references to other projects.
