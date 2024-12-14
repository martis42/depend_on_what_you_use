[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

- [Depend on what you use (DWYU)](#depend-on-what-you-use-dwyu)
- [Getting started](#getting-started)
  - [Get a release](#get-a-release)
  - [Get a specific commit](#get-a-specific-commit)
  - [Use DWYU](#use-dwyu)
- [Applying automatic fixes](#applying-automatic-fixes)
- [Assumptions of use](#assumptions-of-use)
- [Known problems](#known-problems)
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

The DWYU aspect is created in your project by a [factory function offering various options](docs/dwyu_aspect.md) to configure the aspect.
Various illustrations for configuring and using the DWYU aspect can be seen in the [examples](/examples).

Example `.bzl` file creating a DWYU aspect with default configuration:

```starlark
load("@depend_on_what_you_use//:defs.bzl", "dwyu_aspect_factory")

your_dwyu_aspect = dwyu_aspect_factory()
```

### Use the aspect

Assuming you created the DWYU aspect in file `//:aspect.bzl`, execute it on a target pattern:<br>
`bazel build --aspects=//:aspect.bzl%your_dwyu_aspect --output_groups=dwyu <target_pattern>`

If no problem is found, the command will exit with `INFO: Build completed successfully`.<br>
If a problem is detected, the build command will fail with an error and a description of the problem will be printed in the terminal.
For example:

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

# Applying automatic fixes

> [!WARNING]
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

Discovering the DWYU report files automatically can take a large amount of time if the `bazel-bin` directory is too large.
In such cases you can pipe the command line output of executing the DWYU aspect into a file and forward this file to the apply_fixes script via the `--dwyu-log-file` option.
The apply_fixes script will then deduce the DWYU report file locations without crawling though thw whole `bazel-bin` directory.

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

# Known problems

## Preprocessor statements

DWYU does not compile the code, but parses it as text and searches for include statements.
If preprocessor statements control how the code should be interpreted, this is a flawed approach (e.g. include different headers based on the platform).
To work around this DWYU uses [`pcpp`](https://github.com/ned14/pcpp) to preprocess files before searching for include statements.

In most cases this approach works as desired.
There are however some edge cases to be aware of:

1)<br>
`pcpp` is not the preprocessor used by your C++ toolchain.
There is no guarantee that it behaves exactly the same.

2)<br>
DWYU can only forward defined values to `pcpp` which are part of the compiler command build by Bazel.
Some values are however set internally by the compiler while processing files and are unknown to DWYU.<br>
Common cases for such macros can be seen at [cppreference.com](https://en.cppreference.com/w/cpp/preprocessor/replace#Predefined_macros).
While DWYU cannot generally know the values of all those compiler defined macros, we offer a feature to set `__cplusplus` based on a heuristic.

# Supported Platforms

### Aspect

| Platform         | Constraints                                                                   |
| ---------------- | ----------------------------------------------------------------------------- |
| Operating system | Integration tests check [Ubuntu 24.04, Macos 15, Windows 2022].               |
| Python           | Minimum version is 3.8. Integration tests check [3.8, 3.9, 3.10, 3.11, 3.12]. |
| Bazel            | Minimum version is 6.0.0. Integration tests check [6.x, 7.x, 8.x, rolling].   |

### Applying fixes

| Platform         | Constraints                                                     |
| ---------------- | --------------------------------------------------------------- |
| Operating system | Integration tests check [Ubuntu 24.04, Macos 15, Windows 2022]. |
| Python           | Minimum version is 3.8. Integration tests check 3.8.            |
| Bazel            | No known constraint. Integration tests check 7.4.1.             |
| Buildozer        | No known constraint. Integration tests check 6.4.0.             |

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
- How to include DWYU in your project might change at any time.

# Contributing

See [Contributing](CONTRIBUTING.md).

# License

Copyright © 2022-present, [Martin Medler](https://github.com/martis42). <br>
This project licensed under the [MIT](https://opensource.org/licenses/MIT) license.

This projects references several other projects which each have individual licenses.
See the content of [third_party](third_party) for all references to other projects.
