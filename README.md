- [Depend on what you use (DWYU)](#depend-on-what-you-use-dwyu)
- [Getting started](#getting-started)
  - [Get a release](#get-a-release)
  - [Get a specific commit](#get-a-specific-commit)
  - [Use DWYU](#use-dwyu)
- [Features](#features)
  - [Custom header ignore list](#custom-header-ignore-list)
  - [Skipping Targets](#skipping-targets)
  - [Recursion](#recursion)
  - [Implementation_deps](#Implementation_deps)
  - [Known limitations](#known-limitations)
  - [Applying automatic fixes](#applying-automatic-fixes)
- [Supported Platforms](#supported-platforms)
- [Preconditions](#preconditions)
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
  private dependencies for `cc_library`. For more details see [features chapter Implementation_deps](#Implementation_deps).

More information about the idea behind DWYU and the implementation of the project is available in [the docs](docs/).

# Getting started

## Get a release

Choose a release from the [release page](https://github.com/martis42/depend_on_what_you_use/releases) and follow the instructions.

## Get a specific commit

Put the following into your `WORKSPACE` file to use a specific DWYU commit:

```starlark
load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

dwyu_version = "<git_commit_hash>"
http_archive(
    name = "depend_on_what_you_use",
    sha256 = "<archive_checksum>",  # optional
    strip_prefix = "depend_on_what_you_use-{}".format(dwyu_version),
    url = "https://github.com/martis42/depend_on_what_you_use/archive/{}.tar.gz".format(dwyu_version),
)

load("@depend_on_what_you_use//:setup_step_1.bzl", dwyu_setup_step_1 = "setup_step_1")
dwyu_setup_step_1()

load("@depend_on_what_you_use//:setup_step_2.bzl", dwyu_setup_step_2 = "setup_step_2")
dwyu_setup_step_2()

load("@depend_on_what_you_use//:setup_step_3.bzl", dwyu_setup_step_3 = "setup_step_3")
dwyu_setup_step_3()
```

## Use DWYU

### Configure the aspect

Configure an aspect with the desired behavior.
The features which can be configured through the aspect factory attributes are documented at [Features](#features).
Put the following inside a `aspect.bzl` file (file name is exemplary):

```starlark
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

By default, DWYU ignores all header from the standard library when comparing include statements to the dependencies.
This list of headers can be seen in [std_header.py](src/analyze_includes/std_header.py).

You can exclude a custom set of header files by providing a config file in json format to the aspect:

```starlark
your_aspect = dwyu_aspect_factory(config = "//<your_config_file>.json")
```

The config file can contain these fields which should be lists of strings. All fields are optional:

| Field                        | Description                                                                                                                                                                                                                                                                                                   |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ignore_include_paths`       | List of include paths which are ignored by the analysis. Setting this **disables ignoring the standard library include paths**.                                                                                                                                                                               |
| `extra_ignore_include_paths` | List of include paths which are ignored by the analysis. If `ignore_include_paths` is specified as well, both list are combined. If `ignore_include_paths` is not set, the default list of standard library headers is extended.                                                                              |
| `ignore_include_patterns`    | List of patterns for include paths which are ignored by the analysis. Patterns have to be compatible to Python [regex syntax](https://docs.python.org/3/library/re.html#regular-expression-syntax). The [match](https://docs.python.org/3/library/re.html#re.match) function is used to process the patterns, |

Examples and the correct format can be seen at the [custom config test cases](test/aspect/custom_config).

## Skipping targets

If you want the DWYU aspect to skip certain targets and negative target patterns are not an option you can do so by
setting the `no-dwyu` tag on those.

## Recursion

By default, DWYU analyzes only the target it is being applied to.

You can also activate recursive analysis. Meaning the aspect analyzes recursively all dependencies of the target it is
being applied to:

```starlark
your_aspect = dwyu_aspect_factory(recursive = True)
```

This can be used to create a rule invoking DWYU on a target and all its dependencies as part of a normal build command.
Also, it can be a convenience to analyze specific fraction of your stack without utilizing bazel (c)query.

Examples for this can be seen at the [recursion test cases](test/aspect/recursion).

## Implementation_deps

Starting with version 5.0.0 Bazel offers experimental feature [`implementation_deps`](https://docs.bazel.build/versions/5.0.0/be/c-cpp.html#cc_library.implementation_deps)
to distinguish between public (aka interface) and private (aka implementation) dependencies for `cc_library`.
Headers from the private dependencies are not made available to users of the library to trim down dependency trees.

DWYU analyzes the usage of headers from the dependencies and can raise an error if a dependency is used only in
private files, but not put into the private dependency attribute. Meaning, it can find dependencies which should be
moved from `deps` to `implementation_deps`.

Activate this behavior via:

```starlark
your_aspect = dwyu_aspect_factory(use_implementation_deps = True)
```

Examples for this can be seen at the [implementation_deps test cases](test/aspect/implementation_deps).

## Known limitations

- If includes are added through a macro, this is invisible to DWYU.
- Fundamental support for processing preprocessor defines is present.
  However, if header A specifies a define X and is included in header B, header B is not aware of X from header A.
  Right now only defines specified through Bazel (e.g. toolchain or `cc_*` target attributes) or defines specified
  inside a file itself are used to process a file and discover include statements.
  We aim to resolve this limitation in a future release.
- Include statements utilizing `..` are not recognized if they are used on virtual or system include paths.

## Applying automatic fixes

DWYU offers a tool to automatically fix some detected problems.

⚠
Please note that **the tool cannot guarantee that your build is not being broken** by the changes. Always make sure your
project is still valid after the changes and review the performed changes.

The workflow is the following:

1. Execute DWYU on your workspace. DWYU will create report files containing information about discovered problems in the
   Bazel output directory for each analyzed target.
1. Execute `bazel run @depend_on_what_you_use//:apply_fixes -- <your_options>`. The tool discovers the report files
   generated in the previous step and gathers the problems for which a fix is available. Then,
   [buildozer](https://github.com/bazelbuild/buildtools/blob/master/buildozer/README.md) is utilized to adapt the BUILDS
   files in your workspace.

The `apply_fixes` tool requires you to explicitly choose which kind or errors you want to be fixed. You can see the full
command line interface and more information about the script behavior and limitations by executing:<br>
`bazel run @depend_on_what_you_use//:apply_fixes -- --help`

If the `apply_fixes` tool is not able to discover the report files, this can be caused by the `bazel-bin` convenience
symlink at the workspace root not existing or not pointing to the output directory which was used by to generate the
report files. The tool offers options to control how the output directory is discovered.

Unfortunately, the tool cannot promise perfect results due to various constraints:

- If alias targets are involved, this cannot be processed properly. Alias targets are resolved to their actual target
  before the DWY aspect is running. Thus, the DWYU report file contains the actual targets in its report and buildozer
  is not able to modify the BUILD files containing the alias name.
- Buildozer is working on the plain BUILD files as a user would see them in the editor. Meaning without alias resolution
  or macro expansion. Consequently, buildozer cannot work on targets which are generated inside a macro or whose name
  is constructed in a list comprehension.
- Generally the fixes should not break your build. But there are edge cases. For example a dependency X might be unused
  in library A, but the downstream user of library A transitively depends on it. Removing the unused dependency from
  library A will break the build as the downstream dependency no longer finds dependency X.
- Adding missing direct dependencies is based on a heuristic and not guaranteed to find the correct dependency. Also
  analyzing the visibility of potential direct dependencies is not yet implemented, which can cause a broken build if
  a target without the proper visibility is chosen.

# Preconditions

**The code has to be compilable** </br>
DWYU is not performing a compilation itself. It works by statically analyzing the source code and build tree. However,
non compiling code can contain errors which infringe the assumptions DWYU is based on. For example, including header
files which do not exist at the expected path.

**Include paths have to be unambiguous** </br>
In other words, there shall not be multiple header files in the dependency tree of a target matching an
include statement. Even if analysing the code works initially, it might break at any time if the ordering of paths in
the analysis changes.

# Supported Platforms

TODO 3.8

- Assignment expressions
- f-strings support = for self-documenting expressions and debugging
- shlex useful?

| Platform         | Constraints                                                                                      |
| ---------------- | ------------------------------------------------------------------------------------------------ |
| Operating system | No constraints. However, Ubuntu 20.04 is currently the only OS used for development and testing. |
| Python           | Minimum version is 3.8. Tests are currenntly only performed with 3.8.                            |
| Bazel            | Minimum version is 5.0.0. Multiple versions are tested.                                          |
| Buildozer        | No known limitations. Tests have been performed with 5.0.1.                                      |

# Alternatives to DWYU

To make sure no headers from transitive dependencies or private headers from dependencies are used you can use
[Layering check with Clang](https://maskray.me/blog/2022-09-25-layering-check-with-clang) which is natively supported by Bazel.
This approach has some benefits over DWYU:

- Directly integrated into Bazel without need for further tooling.
- Is able to overcome [the known DWYU limitations](#known-limitations).

Still, there are reasons to use DWYU instead of or in addition to layering_check:

- DWYU Does not require a compiler, it works purely by text parsing.
  This is the reason for some of it's [the known DWYU limitations](#known-limitations).
  However, this also makes the tool more flexible and independent of your platform.
  For example when using a recent clang version is not possible for you.
- DWYU detects unused dependencies.
- DWYU allows optimizing [implementation_deps](#implementation_deps).
- DWYU offers automatic fixes for detected issues.

# Versioning

This project uses [semantic versioning](https://semver.org/spec/v2.0.0.html).
Please be aware that the project is still in an early phase and until version 1.0.0 has been reached all releases
can contain breaking changes.

The report files DWYU generates to facilitate running automatic fixes are considered an implementation detail.
Changing their content is not considered a breaking change.
You are of course free to use those report files in custom scripts of yours, but might have to adapt those scripts
also for minor version updates.

Also, how to include DWYU in your WORKSPACE file might change at any time.

# Contributing

See [Contributing](CONTRIBUTING.md).

# License

Copyright © 2022-present, [Martin Medler](https://github.com/martis42). </br>
This project licensed under the [MIT](https://opensource.org/licenses/MIT) license.

This projects references several other projects which each have individual licenses.
See the content of [third_party](third_party) for all references to other projects.
