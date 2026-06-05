[![GitHub release](https://img.shields.io/github/v/release/martis42/depend_on_what_you_use)](https://github.com/martis42/depend_on_what_you_use/releases)
[![BCR](https://img.shields.io/badge/BCR-available-green)](https://registry.bazel.build/modules/depend_on_what_you_use)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-available-brightgreen)](https://github.com/martis42/depend_on_what_you_use/blob/main/docs)
<br>
[![Bazel](https://img.shields.io/badge/Bazel-7.6.0+-green)](https://bazel.build/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Linux](https://img.shields.io/badge/Linux-FCC624?logo=linux&logoColor=black)](<>)
[![macOS](https://img.shields.io/badge/macOS-000000?logo=apple&logoColor=white)](<>)
[![Windows](https://img.shields.io/badge/Windows-0078D6?logo=windows&logoColor=white)](<>)
<br>
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![ty](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json)](https://github.com/astral-sh/ty)
[![clang-tidy](https://img.shields.io/badge/clang--tidy-used-blue)](https://clang.llvm.org/extra/clang-tidy/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

- [Depend on what you use (DWYU)](#depend-on-what-you-use-dwyu)
- [Getting started](#getting-started)
- [Applying automatic fixes](#applying-automatic-fixes)
- [Assumptions of use](#assumptions-of-use)
- [Supported Platforms](#supported-platforms)
- [Known limitations](#known-limitations)
- [Troubleshooting](#troubleshooting)
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
  This has to be explicitly enabled.
  See the [aspect documentation](docs/api/dwyu_aspect.md) for further details.

More information about the idea behind DWYU and the implementation of the project is available in [the docs](docs).

# Getting started

## Get DWYU

Choose a release from the [release page](https://github.com/martis42/depend_on_what_you_use/releases) and follow the instructions.

To use a specific commit, put the following into your `MODULE.bazel` file

```starlark
bazel_dep(name = "depend_on_what_you_use")
git_override(
    module_name = "depend_on_what_you_use",
    commit = <commit_you_are_interested_in>,
    remote = "https://github.com/martis42/depend_on_what_you_use",
)
```

## Use DWYU

### Configure the aspect

The DWYU aspect is created in your project by a [factory function offering various options](docs/api/dwyu_aspect.md) to configure the aspect.
Various illustrations for configuring and using the DWYU aspect can be seen in the [examples](/examples).

Example `.bzl` file creating a DWYU aspect with default configuration:

```starlark
load("@depend_on_what_you_use//dwyu/cc:defs.bzl", "dwyu_cc_aspect_factory")

your_dwyu_aspect = dwyu_cc_aspect_factory()
```

### Use the aspect

Assuming you created the DWYU aspect in file `//:aspect.bzl`, execute it on a target pattern:<br>
`bazel build --aspects=//:aspect.bzl%your_dwyu_aspect --output_groups=dwyu <target_pattern>`

If no problem is found, the command will return successfully without further output.<br>
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

**Hint**: Using `--keep_going` allows you to see all existing errors at once instead of the analysis aborting on the first detected issue.

### Create a rule invoking the aspect

You can invoke the aspect from within a rule.
This can be useful to make the execution part of a bazel build on dedicated targets without having to manually execute the longish aspect build command.

The Bazel documentation for invoking an aspect from within a rule can be found [here](https://bazel.build/rules/aspects#invoking_the_aspect_from_a_rule).

This is demonstrated in the [rule_using_dwyu example](/examples/rule_using_dwyu).

# Applying automatic fixes

> [!WARNING]
> Please note that **the tool cannot guarantee that your build is not being broken** by the changes.
> Always make sure your project is still valid after the changes and review the performed changes.

> [!NOTE]
> This tool is executing Bazel commands.
> If one needs to configure bazel commands with custom options in your workspace, please have a look at the `--bazel-args` and `--bazel-startup-args` options of this tool.

DWYU offers a tool to automatically fix some detected problems.
The general workflow is the following:

1. Execute DWYU on your workspace.
   DWYU will create report files containing information about discovered problems in the Bazel output directory.
1. Execute `bazel run @depend_on_what_you_use//dwyu/apply_fixes:apply_fixes -- <your_options>`.
   The tool discovers the report files generated in the previous step and gathers the problems for which a fix is available.
   Then, [buildozer](https://github.com/bazelbuild/buildtools/blob/master/buildozer/README.md) is utilized to adapt the BUILD files in your workspace.

We recommend:

- Execute the DWYU analysis build with `--keep_going` to generate the DWYU reports to find all issues at once.
- Pipe the terminal output from executing DWYU into a file.
  Then, provide this log file to `@depend_on_what_you_use//dwyu/apply_fixes:apply_fixes` via the `--dwyu-log-file` option.
  This is the fastest and most robust option to make the DWYU reports available to the `apply_fixes` tool.

The `apply_fixes` tool requires you to explicitly choose which kind or errors you want to be fixed.
You can see the full command line interface and more information about the script behavior and limitations by executing:<br>
`bazel run @depend_on_what_you_use//dwyu/apply_fixes:apply_fixes -- --help`

If you are not using `--dwyu-log-file`, the `apply_fixes` tool searches by itself for the DWYU reports in the output base, which can be slow for large workspaces.

Unfortunately, the tool cannot promise perfect results due to various constraints:

- If alias targets are involved, this cannot be processed properly.
  Alias targets are resolved to their actual target before the DWYU aspect is running.
  Thus, the DWYU report file contains the actual targets in its report and buildozer is not able to modify the BUILD files containing the alias name.
- Buildozer is working on the plain BUILD files as a user would see them in the editor.
  Meaning without alias resolution or macro expansion.
  Consequently, buildozer cannot work on targets which are generated inside a macro or whose name is constructed.
- Adding missing direct dependencies is based on a heuristic and not guaranteed to find the correct dependency.

# Assumptions of use

##### The code has to be compilable

DWYU assumes the code under inspection compiles with the Bazel configuration used to execute DWYU (e.g. setting `--config=foo`).
There is no guarantee DWYU will do something meaningful for non compilable code.

##### Include paths have to be unambiguous

There shall not be multiple header files in the dependency tree of a target matching an include statement.
Even if analyzing the code works initially, it might break at any time if the ordering of paths in the analysis changes.

# Supported Platforms

**Linux** is fully supported.<br>
All tests and quality checks run on GitHub Ubuntu workers.

**Macos** and **Windows** are supported on a best effort basis.<br>
All our integration tests run on GitHub Macos and Windows workers.
Bugs we can reproduce via the CI workers with reasonable effort will be fixed.

### Aspect

| Tool  | Constraints                                                                                      |
| ----- | ------------------------------------------------------------------------------------------------ |
| C++   | Minimum required C++ standard is C++11.                                                          |
| Bazel | Minimum required version is 7.6.0. We test all supported major versions and the rolling release. |

### Applying fixes

| Tool   | Constraints                                                                                                |
| ------ | ---------------------------------------------------------------------------------------------------------- |
| Python | Integration tests check 3.10.                                                                              |
| Bazel  | No known constraint. Integration tests check the Bazel version defined in [.bazelversion](/.bazelversion). |

# Known limitations

DWYU has some limitations.
You find the details about those in [these docs](docs/project/known_limitations.md).

# Troubleshooting

When encountering problems while using DWYU, you find common problems and suggested solutions in [these docs](docs/project/troubleshooting.md).

# Alternatives to DWYU

## Layering check

To make sure no headers from transitive are used you can use [Layering check with Clang](https://maskray.me/blog/2022-09-25-layering-check-with-clang), which is natively supported by Bazel.
An example for a CC toolchain supporting this feature is https://github.com/bazel-contrib/toolchains_llvm.
The main benefit of this approach is it being directly integrated into Bazel without need of further tooling like DWYU.

Still, there are reasons to consider using DWYU instead of or in addition to layering_check:

- DWYU does not require a full compilation, it only executes the preprocessing step.
- DWYU is able to analyze header only libraries.
- DWYU is not limited to LLVM based toolchains (`layering_check` is based on LLVM's implementation of modules).
- DWYU detects unused dependencies.
- DWYU allows optimizing the usage of [implementation_deps](#implementation_deps).
- DWYU offers automatic fixes for detected issues.

## Gazelle

[Gazelle](https://github.com/bazelbuild/bazel-gazelle) is a tool automatically creating `BUILD` files for your code.
`rules_cc` does not offer a standard Gazelle plugin for C/C++.
However, another party open sourced [gazelle_cc](https://github.com/EngFlow/gazelle_cc) to provide Gazelle support for C/C++.

Automatically generating correct BUILD files based on your source code is a more efficient approach compared to executing DWYU regularly to make sure no error was introduced.

A reason for using DWYU instead of `gazelle_cc` can be if your project uses conditional include statements based on custom conditions.
According to [their documentation](https://github.com/EngFlow/gazelle_cc#-gazellecc_platform-os-arch-constraint_label-macrovalue-), `gazelle_cc` is only supporting \<os> and \<arch> based conditional includes.

# Versioning

This project uses [semantic versioning](https://semver.org/spec/v2.0.0.html).

The following things specifically are not considered breaking changes:

- The report files DWYU generates to facilitate running automatic fixes are considered an implementation detail.
- Raising the minimum required version for a dependency or Bazel.

# Contributing

See [Contributing](CONTRIBUTING.md).

# License

Copyright © 2022-present, [Martin Medler](https://github.com/martis42). <br>
This project licensed under the [MIT](https://opensource.org/licenses/MIT) license.

This projects references several other projects which each have individual licenses.
See the content of [third_party](third_party) and [MODULE.bazel](MODULE.bazel) for all references to other projects.
