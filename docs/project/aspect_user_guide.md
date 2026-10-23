<!-- mdformat-toc start --slug=github --maxlevel=2 --minlevel=1 -->

- [Guide for using and configuring DWYU](#guide-for-using-and-configuring-dwyu)
  - [1. How to use the DWYU tool](#1-how-to-use-the-dwyu-tool)
  - [2. Target selection](#2-target-selection)
  - [3. Available checks and their configuration](#3-available-checks-and-their-configuration)
  - [4. Targets that cannot comply with DWYU's rules](#4-targets-that-cannot-comply-with-dwyus-rules)
  - [5. Preprocessing](#5-preprocessing)
  - [6. Executing DWYU on specific targets during normal builds](#6-executing-dwyu-on-specific-targets-during-normal-builds)

<!-- mdformat-toc end -->

# Guide for using and configuring DWYU<a name="guide-for-using-and-configuring-dwyu"></a>

This guide explains common use cases for using and configuring DWYU.
All DWYU aspect options are documented in the [aspect documentation](/docs/api/dwyu_aspect.md).<br>
See the [troubleshooting guide](/docs/project/troubleshooting.md) for issues that do not fit clearly in this guide.

## 1. How to use the DWYU tool<a name="1-how-to-use-the-dwyu-tool"></a>

DWYU is a Bazel [aspect](https://bazel.build/extending/aspects).

Run `bazel build` with the `--aspects=//<file_holding_the_configured_aspect>%<aspect_name>` and `--output_groups=dwyu` options to request DWYU analysis.
Bazel executes the actions registered by the aspect, along with any build actions needed to produce their inputs, such as compiling the DWYU tool or generating files in your stack.

The DWYU aspect is created and configured in a .bzl file in your project with the factory function offered by DWYU.

```starlark
load("@depend_on_what_you_use//dwyu/cc:defs.bzl", "dwyu_cc_aspect_factory")

# Providing no arguments means using the default configuration
dwyu = dwyu_cc_aspect_factory()
dwyu_with_custom_options = dwyu_cc_aspect_factory(analysis_optimizes_impl_deps = True, recursive = True)
```

We recommend registering a `dwyu` configuration in your `.bazelrc` file to set the aspect and output group.
If the aspect definition above is saved in `tools/dwyu/aspect.bzl`, the configuration looks like this:

```
build:dwyu --aspects=//tools/dwyu/aspect.bzl%dwyu
build:dwyu --output_groups=dwyu
build:dwyu <optional_project_specific_bazel_options_you_always_want_together_with_dwyu>
```

**Hint**: We recommend you perform the DWYU builds with Bazel option `--keep_going` to ensure you see all existing findings at once instead of aborting on each single discovered issue.

When the DWYU analysis is a success you see no DWYU specific terminal output and Bazel reports a successful build.
If the DWYU analysis finds an issue Bazel will report a failed build and you will see some output similar to this one:

```
================================================================================
DWYU analyzing: '<analyzed_target>'

Result: Failure

Unused dependencies in 'deps' (none of their headers are referenced):
  Dependency='//some/target/with_an_unused:dependency'
===============================================================================
```

## 2. Target selection<a name="2-target-selection"></a>

### A target pattern

No special configuration is required.
Simply build the target pattern with `--config=dwyu`.<br>
For example: `bazel build --config=dwyu //some/targets/...`.

### A target pattern including its whole dependency tree

By default, DWYU analyzes only the targets matching the target pattern given to the build command.
If you want to analyze all transitive dependencies of the target pattern as well, you can do so by using the DWYU aspect option `recursive = True`.

Please note, DWYU will also recurse into targets from your external dependencies.
This might cause a lot of findings in code outside of your control.
You can limit recursion to targets from your own workspace with the DWYU aspect option `skip_external_targets = True`.

## 3. Available checks and their configuration<a name="3-available-checks-and-their-configuration"></a>

### Check options

| Aspect option                          | Explanation                                                                                       |
| -------------------------------------- | ------------------------------------------------------------------------------------------------- |
| `analysis_reports_missing_direct_deps` | Report includes not covered by a direct dependency.                                               |
| `analysis_reports_unused_deps`         | Report dependencies whose headers are not included.                                               |
| `analysis_optimizes_impl_deps`         | For `cc_library`, report `deps` used only by files in `srcs`; move them to `implementation_deps`. |

Each check can be enabled or disabled individually.
More information about those and their default values can be seen in the [aspect documentation](/docs/api/dwyu_aspect.md).

### Exceptions to checks

We can configure exceptions for some checks.

#### Skip include statements

Your code might have include statements for which there will never be a direct dependency.
For such cases, create a JSON file specifying include paths or patterns for DWYU to skip.
The schema for this JSON file and its full documentation can be found under the `ignored_includes` DWYU aspect option in the [aspect documentation](/docs/api/dwyu_aspect.md).

#### Ignoring unused dependencies

Your stack might have targets that must be dependencies even if none of their headers are used.
Use the `ignored_unused_deps` DWYU aspect option to provide a list of such targets for which _unused dependency_ findings are never reported.

### Usage of private headers

Strictly speaking, header files listed in `srcs` of a `cc_library` should not be used by consumers of the library.
This is not just a DWYU design decision; it follows the upstream [`cc_*` rules design](https://bazel.build/reference/be/c-cpp#hdrs).<br>
Unfortunately, the Bazel CC toolchains don't enforce this rule and thus many projects violate it.

By default DWYU follows the intended `cc_*` rules design.
That means, in its analysis DWYU ignores header files from the `srcs` attribute of `cc_library` dependencies.

If your stack does not follow this `cc_*` rules design, you can tell DWYU to also consider headers from the `srcs` attribute of `cc_library` dependencies.
You do so by using the `analysis_ignores_private_headers_from_deps = False` DWYU aspect option.

## 4. Targets that cannot comply with DWYU's rules<a name="4-targets-that-cannot-comply-with-dwyus-rules"></a>

Not all targets in your stack may be able to follow the rules enforced by DWYU.
Some targets may intentionally use a different design, or an external dependency may be modeled in a way that is incompatible with DWYU's expectations.

### Excluding targets

All `skip_*` DWYU aspect options exclude targets from the DWYU analysis.
They are mostly self-explanatory and are not explained in detail here.
Examples using those options can be seen in the [skipping targets examples](/examples/skipping_targets).

### Targets designed to forward headers

A target might be designed to forward its dependencies' headers to its users.
This violates the DWYU principle of "_always depend directly on the targets providing the headers you use_".
Still, DWYU can work with such targets, if we configure DWYU accordingly.

We can tell DWYU that it should treat target _FOO_ as if it were providing itself the header files of target _BAR_.
This is done by setting up a [target mapping](/docs/api/cc_info_mapping.md).
A target mapping is a dedicated Bazel target using the `dwyu_make_cc_info_mapping` rule.
How to use this rule exactly and in which ways targets can be mapped on each other is explained in the [target mapping documentation](/docs/api/cc_info_mapping.md).
The naming difference of _CcInfo mapping_ vs. _target mapping_ is a case of bad naming in the early phase of the project.
The implementation merges `CcInfo` providers, but the user-facing behavior is that we virtually map the headers provided by one target onto another target.<br>
After setting up a target mapping, pass it to the DWYU aspect with the `target_mapping` option.

## 5. Preprocessing<a name="5-preprocessing"></a>

### The problem

DWYU does not compile your code, it only extracts the include statements from your files and compares them to the headers provided by your dependencies.
Include statements can however depend on the preprocessor and the build config, so called "_conditional includes_".
For example this header file and the associated BUILD file:

```cpp
#ifdef USE_FANCY_BACKEND
#include "fancy_backend.h"
#else
#include "simple_backend.h"
#endif
```

```starlark
cc_library(
    name = "foo",
    hdrs = ["use_backend.h"],
    defines = select({
        "//condition_for:fancy_backend": ["USE_FANCY_BACKEND"],
        "//conditions:default": [],
    }),
    deps = select({
        "//condition_for:fancy_backend": ["//target/providing:fancy_backend"],
        "//conditions:default": ["//target/providing:simple_backend"],
    }),
)
```

Which of the two headers is really used depends on the build configuration.
Simply extracting all `#include ..` statements, like the DWYU aspect option `preprocessing_mode` default value `fast` does, will always report one header is included without a corresponding direct dependency.

### How DWYU handles it

The DWYU aspect option `preprocessing_mode` controls how include statements are extracted:

| `preprocessing_mode`     | Behavior                                                                                                                        | Prefer it when                                                         |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| `fast` (default)         | Extracts all include statements, ignoring preprocessor statements                                                               | Your include statements do not depend on conditions or macros          |
| `ignore_system_includes` | Preprocesses files with `boost::wave`, but does not look into headers included via `<...>` and ignores the CC toolchain headers | You use conditional includes and want preprocessing at a moderate cost |
| `full`                   | Preprocesses files with `boost::wave` and recursively all included headers, except the CC toolchain headers                     | Conditional includes based on values from headers included via `<...>` |

The preprocessing modes `full` and `ignore_system_includes` are significantly slower than `fast`.
We recommend starting with `fast` and switching to preprocessing only if you actually see findings caused by conditional includes.

Using `fast` is also fine for conditional includes if each branch's dependency is available in all configurations.
It stops working when a `select()` switches the dependencies, as the include of the inactive branch is then reported as missing.

### Dealing with unsupported constructs

Preprocessing with `boost::wave` has limits.
Some constructs cannot be handled, which can lead to include statements being missed and dependencies falsely reported as unused.
The `preprocessing_fallback = True` option makes DWYU fall back to the `fast` behavior for exactly those files, while all others are still preprocessed.
Using `verbose = True` shows for which files the fallback was used.
This trades conditional include resolution for those files against never losing include statements.

The unsupported constructs are listed in the [known limitations](/docs/project/known_limitations.md#missing-preprocessor-features).

### Macros unknown to Bazel

DWYU only knows the macros Bazel passes to the compiler.
Macros set internally by the compiler or the standard library are unknown to it, and conditional includes depending on them cannot be resolved correctly.
Options are to make the macro known via `--cxxopt=-D...` in your DWYU Bazel config, or to use `fast`.
Details are in the [known limitations](/docs/project/known_limitations.md#conditional-include-statements-based-on-unknown-macros).

### Choosing a preprocessing mode

1. No conditional includes: keep `fast`.
1. Conditional includes depending on macros set by Bazel: use `ignore_system_includes`; use `full` only if needed.
1. Conditional includes depending on macros unknown to Bazel: define the macros for the DWYU config, otherwise stay on `fast`.

See the [aspect documentation](/docs/api/dwyu_aspect.md) for how individual targets can override this setting with the `dwyu:preprocessing_mode=<mode>` tag.

## 6. Executing DWYU on specific targets during normal builds<a name="6-executing-dwyu-on-specific-targets-during-normal-builds"></a>

You can invoke the DWYU aspect from within a rule.
This can be useful to make the execution part of a bazel build on dedicated targets without having to execute the aspect based build command in a dedicated step.

The Bazel documentation for invoking an aspect from within a rule can be found [here](https://bazel.build/rules/aspects#invoking_the_aspect_from_a_rule).
This is demonstrated in the [rule_using_dwyu example](/examples/rule_using_dwyu).
