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
[![prek](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/j178/prek/master/docs/assets/badge-v0.json)](https://github.com/j178/prek)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/martis42/depend_on_what_you_use/badge)](https://scorecard.dev/viewer/?uri=github.com/martis42/depend_on_what_you_use)

<!-- mdformat-toc start --slug=github --maxlevel=1 --minlevel=1 -->

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

<!-- mdformat-toc end -->

# Depend on what you use (DWYU)<a name="depend-on-what-you-use-dwyu"></a>

DWYU is a Bazel aspect for C++ projects making sure the headers your Bazel targets are using are aligned with their dependency lists.

DWYUs enforces the design principle:<br>
**A `cc_*` target _X_ shall depend directly on the targets providing the header files which are included in the source code of _X_.**

The main features are:

- Finding include statements which are not available through a direct dependency, aka **preventing to rely on transitive dependencies for includes**.
- Finding unused dependencies.
- Given one uses [`implementation_deps`](https://bazel.build/reference/be/c-cpp#cc_library.implementation_deps), making sure one distinguishes properly between public and private dependencies for `cc_library` targets.
  This has to be explicitly enabled.
  See the [aspect documentation](docs/api/dwyu_aspect.md) for further details.

More information about the idea behind DWYU and the implementation of the project is available in [the docs](/docs).

# Getting started<a name="getting-started"></a>

## Get DWYU<a name="get-dwyu"></a>

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

## Use DWYU<a name="use-dwyu"></a>

DWYU is a Bazel aspect.
You configure it by creating an aspect in your workspace with a factory function and then performing a bazel build command.
If DWYU detects no issues you see a successful bazel build.
When DWYU discovers an error, you see a failed build and an error message explaining the problem.

The [user guide](/docs/project/aspect_user_guide.md) contains a full walkthrough how to configure and use the DWYU aspect.
Also, we have some [examples](/examples).

# Applying automatic fixes<a name="applying-automatic-fixes"></a>

DWYU offers a tool to automatically fix some detected problems.
See this [documentation](/docs/project/automatic_fixes.md).

# Assumptions of use<a name="assumptions-of-use"></a>

#### The code has to be compilable<a name="the-code-has-to-be-compilable"></a>

DWYU assumes the code under inspection compiles with the Bazel configuration used to execute DWYU (e.g. setting `--config=foo`).
There is no guarantee DWYU will do something meaningful for non compilable code.

This also applies to header only code.
Meaning, we assume a header only library depends directly or transitively on all headers it uses.
A header only library using a header which is not in its dependency tree is something we consider a violation of our assumptions of use.

#### Include paths have to be unambiguous<a name="include-paths-have-to-be-unambiguous"></a>

There shall not be multiple header files in the dependency tree of a target matching an include statement.
Even if analyzing the code works initially, it might break at any time if the ordering of paths in the analysis changes.

# Supported Platforms<a name="supported-platforms"></a>

**Linux** is fully supported.<br>
All tests and quality checks run on GitHub Ubuntu workers.

**Macos** and **Windows** are supported on a best effort basis.<br>
All our integration tests run on GitHub Macos and Windows workers.
Bugs we can reproduce via the CI workers with reasonable effort will be fixed.

### Aspect<a name="aspect"></a>

| Tool  | Constraints                                                                                      |
| ----- | ------------------------------------------------------------------------------------------------ |
| C++   | Minimum required C++ standard is C++11.                                                          |
| Bazel | Minimum required version is 7.6.0. We test all supported major versions and the rolling release. |

### Applying fixes<a name="applying-fixes"></a>

| Tool   | Constraints                                                                                                |
| ------ | ---------------------------------------------------------------------------------------------------------- |
| Python | Integration tests check 3.10.                                                                              |
| Bazel  | No known constraint. Integration tests check the Bazel version defined in [.bazelversion](/.bazelversion). |

# Known limitations<a name="known-limitations"></a>

DWYU has some limitations.
You find the details about those in [these docs](docs/project/known_limitations.md).

# Troubleshooting<a name="troubleshooting"></a>

When encountering problems while using DWYU, you find common problems and suggested solutions in [these docs](docs/project/troubleshooting.md).

# Alternatives to DWYU<a name="alternatives-to-dwyu"></a>

## Layering check<a name="layering-check"></a>

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

## Gazelle<a name="gazelle"></a>

[Gazelle](https://github.com/bazelbuild/bazel-gazelle) is a tool automatically creating `BUILD` files for your code.
`rules_cc` does not offer a standard Gazelle plugin for C/C++.
However, another party open sourced [gazelle_cc](https://github.com/EngFlow/gazelle_cc) to provide Gazelle support for C/C++.

Automatically generating correct BUILD files based on your source code is a more efficient approach compared to executing DWYU regularly to make sure no error was introduced.

A reason for using DWYU instead of `gazelle_cc` can be if your project uses conditional include statements based on custom conditions.
According to [their documentation](https://github.com/EngFlow/gazelle_cc#-gazellecc_platform-os-arch-constraint_label-macrovalue-), `gazelle_cc` is only supporting \<os> and \<arch> based conditional includes.

# Versioning<a name="versioning"></a>

This project uses [semantic versioning](https://semver.org/spec/v2.0.0.html).

The following things specifically are not considered breaking changes:

- The report files DWYU generates to facilitate running automatic fixes are considered an implementation detail.
- Raising the minimum required version for a dependency or Bazel.

Our interpretation of _backwards incompatible change_ is the behavior changing without the user being able to trivially adapt.
Meaning, we will rename config options or change default values in minor version bumps, since the user can trivially adapt things in the DWYU config.
Only removing an option without replacement or changing the behavior without possibility to configure the old behavior are considered breaking changes on major version level.

# Contributing<a name="contributing"></a>

See [Contributing](/CONTRIBUTING.md).

# License<a name="license"></a>

Copyright © 2022-present, [Martin Medler](https://github.com/martis42). <br>
This project licensed under the [MIT](https://opensource.org/licenses/MIT) license.

This projects references several other projects which each have individual licenses.
See the content of [third_party](/third_party) and [MODULE.bazel](/MODULE.bazel) for all references to other projects.
