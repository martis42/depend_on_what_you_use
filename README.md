[![GitHub release](https://img.shields.io/github/v/release/martis42/depend_on_what_you_use)](https://github.com/martis42/depend_on_what_you_use/releases)
[![BCR](https://img.shields.io/badge/BCR-available-green)](https://registry.bazel.build/modules/depend_on_what_you_use)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-available-brightgreen)](https://github.com/martis42/depend_on_what_you_use/blob/main/docs)
<br>
[![Bazel](https://img.shields.io/badge/Bazel-7.2.1+-green)](https://bazel.build/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
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
  - [Get a release](#get-a-release)
  - [Get a specific commit](#get-a-specific-commit)
  - [Use DWYU](#use-dwyu)
- [Applying automatic fixes](#applying-automatic-fixes)
- [Assumptions of use](#assumptions-of-use)
- [Known limitations](#known-limitations)
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
  This has to be explicitly enabled.
  See the [aspect documentation](docs/dwyu_aspect.md) for further details.

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

DWYU assumes the code under inspection compiles with the Bazel configuration used to execute DWYU (e.g. setting `--config=foo`).
There is no guarantee DWYU will do something meaningful for non compilable code.

##### Include paths have to be unambiguous

There shall not be multiple header files in the dependency tree of a target matching an include statement.
Even if analyzing the code works initially, it might break at any time if the ordering of paths in the analysis changes.

# Known limitations

## C++ modules

C++ code using [C++ modules](https://en.cppreference.com/w/cpp/language/modules.html) is not supported by DWYU.

Although, `rules_cc` supports C++ modules by now, this is at the time of writing this a new feature for Bazel C++ projects and not yet widely used.
Also, the preprocessing library [boost wave](https://github.com/boostorg/wave) we depend on is not supporting C++ modules.

## Some cases of conditional include statements

DWYU does not compile the code.
It uses a preprocessor library to parse it and extract the relevant include statements.

This approach is flawed, as this DWYU preprocessing step is not doing the exact same thing as your Bazel CC toolchain preprocessor due to being a different program.
On top, the DWYU preprocessing step is missing information.
There are a lot of macros defining the platform behavior and system library capabilities, which are not passed on the command line to the compiler but set internally by the compiler.
DWYU does not have access to those values.
For this reason, DWYU skips the Bazel CC toolchain standard library and system headers during reprocessing, as we do not have the information to preprocess them properly.

Consequently, if a project uses conditional include statements based on macros not visible to Bazel, DWYU cannot properly process them.
We consider this however a rare edge case.
Most projects use conditional include statements based on macros set by Bazel to accommodate for variation points in the build process, which DWYU can process just fine.

If your project is impacted by this edge case, you can try some mitigation strategies:

- You can use the `no_preprocessor` DWYU aspect option to disable preprocessing.
  As long as you don't use select statements to dynamically switch between different dependencies for your targets this still allows a proper DWYU analysis.
- You can use `--cxxopt=-DSomeMacro=42` to manually set the missing macro via Bazel to make it known to Bazel.
  This works best if you define a Bazel config for execution the DWYU aspect and make the cxxopt part of the config.

## Specifying include paths via `copts` and similar

Using the C/C++ rules attributes \[`copts`, `conlyopts`, `cxxopts`\] or the command line options \[`--copt`, `--copnlyopt`, `--cxxopt`\] to specify include paths is not supported.
DWYU relies on the information in the `CcInfo` provider to analyze available include paths from dependencies, which does not include information provided via the copt options.

If a targets has to define special include paths, it should use the proper Bazel API via the C/C++ rules attributes \[`includes`, `include_prefix`, `strip_include_prefix`\].
Include paths specified by those attributes are respected by DWYU.

## Framework includes

DWYU considers [framework includes](https://bazel.build/rules/lib/builtins/CompilationContext.html#framework_includes) like system headers or CC toolchain headers and thus does not process them.
Meaning, DWYU assumes those are globally available without the need for explicit dependencies.

# Supported Platforms

**Linux** is fully supported.<br>
All tests and quality checks run on GitHub Ubuntu 24.04 workers.

**Macos** and **Windows** are supported on a best effort basis.<br>
All our integration tests run on GitHub Macos 15 and Windows 2022 workers.
Bugs we can reproduce via the CI workers with reasonable effort without making DWYU significantly worse on Linux will be fixed.

### Aspect

| Tool   | Constraints                                                     |
| ------ | --------------------------------------------------------------- |
| Python | Minimum tested version is 3.8. Maximum tested version is 3.13.  |
| Bazel  | Minimum tested version is 7.2.1. Maximum tested version is 9.x. |

### Applying fixes

| Tool      | Constraints                                                                                                |
| --------- | ---------------------------------------------------------------------------------------------------------- |
| Python    | Integration tests check 3.8.                                                                               |
| Bazel     | No known constraint. Integration tests check the Bazel version defined in [.bazelversion](/.bazelversion). |
| Buildozer | No known constraint. Integration tests check 8.2.1.                                                        |

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
