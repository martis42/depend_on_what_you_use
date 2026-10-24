# Depend on what you use (DWYU) Changelog

This is a human and agent friendly changelog focusing on user facing changes.
Thus, internal refactoring, project maintenance work and so on won't be visible here.

For details about our versioning scheme see the [versioning chapter](/README.md#versioning) in our README.

We use a style close to [keepachangelog](https://keepachangelog.com/en/1.1.0/).
We deviate from this style by having a dedicated section for `BREAKING` breaking changes, so those important changes are easier to spot.

How to read the changelog:

- `BREAKING`: Breaking changes to user facing behavior.
  If a feature is marked as experimental or deprecated, we do not consider changes to it as breaking.
- `Removed`: Remove user facing functionality.
  We do not consider removing something with a drop in replacement with the same functionality as breaking change.
- `Deprecated`: Mark existing user facing functionality as deprecated.
  In future releases it might lose test coverage or might be removed.
- `Changed`: An existing user facing functionality changed in a backwards compatible way.
  We do not consider renaming something to another thing with the same functionality as breaking change.
- `Fixed`: Bug fixes to user facing functionality.
- `Added`: New user facing functionality without non backwards compatible side effects to existing features.
- If changes are scoped to a single sub system, they have a leading keyword in brackets, e.g. `[aspect]`.

## Unreleased

## [1.2.0](https://github.com/martis42/depend_on_what_you_use/releases/tag/1.2.0) - 2026.10.23

### Changed

- [aspect] The default value of option `preprocessing_mode` is now `fast`.
  While the `boost::wave` based modes `full` and `ignore_system_includes` work in most cases, there are some known edge cases.
  Also, they are significantly slower than the `fast` mode.
  Thus, the `preprocessing_mode` values `full` and `ignore_system_includes` should be used only by projects actually utilizing conditional include statements.
- [aspect] Use the C++ standard of the Bazel configuration and CC toolchain when preprocessing with `preprocessing_mode` values `full` or `ignore_system_includes`, instead of always using C++11.
  Please note, if your code uses preprocessor relevant language constructs newer than you project C/C++ language standard and your compiler manages this by some extension mechanism, this won't be parseable by the DWYU preprocessor.
- [target_mapping] The explicit mapping mode in `dwyu_make_cc_info_mapping` has been reworked:
  - You can only map targets from the dependency tree and no longer by accident map unrelated targets.
  - There are no more visibility constraints for the mapped targets.
  - The old single target mapping syntax is still supported for a grace period.
- [target_mapping] The dependencies mapping modes in `dwyu_make_cc_info_mapping` have been reworked:
  - The `MAP_DIRECT_DEPS` and `MAP_TRANSITIVE_DEPS` modes can now be limited to a subset of targets.
  - Mapping all dependencies is now an explicit choice instead of an implicit default.
  - The old syntax to specify mappings is still supported for a grace period.

### Fixed

- [aspect] Properly preprocess raw string literals with the preprocessing modes `full` and `ignore_system_includes`.
- [aspect] Allow code undefining build configuration macros with the preprocessing modes `full` and `ignore_system_includes`.

### Added

- Add a dedicate user guide giving guidance on the most common configuration steps for using DWYU in [dwyu_user_guide.md](/docs/project/dwyu_user_guide.md).
- [aspect] Add new option `preprocessing_fallback`, which makes the preprocessing modes `full` and `ignore_system_includes` fall back to the `fast` mode for files `boost::wave` cannot preprocess properly.
  For some code constructs `boost::wave` fails the preprocessing and our include statement discovery logic breaks.
  With this option enabled, in such a case we rescan the code automatically without preprocessor which might report too many include statements if conditional incudes were used, but never too little.

## [1.1.2](https://github.com/martis42/depend_on_what_you_use/releases/tag/1.1.2) - 2026.08.11

### Changed

- [aspect] Rename `skipped_tags` to `skip_tags`.
  The functionality did not change.
  `skipped_tags` is still usable, but will be removed in a future release and using it prints a warning.

### Fixed

- [aspect] Do not crash on `deps` not providing CcInfo.
- [target_mapping] Skip non existing `deps` attribute while mapping dependencies.
- [apply_fixes] Handle repository-relative `strip_include_prefix`.

### Added

- [aspect] Allow ignoring unused dependencies findings with new option `ignored_unused_deps`.
- [aspect] Allow controlling some aspect settings per single target via tags.
  See [the aspect docs](/docs/api/dwyu_aspect.md) for which options can be controlled by tags.
- [aspect] Add new option `skip_targets` to centrally exclude targets from the DWYU analysis.
- [aspect] Allow controlling with new option `recursion_stops_on_skip` if recursion breaks on skipping a target.
- [aspect] Allow skipping the analysis based on features active for a target with new option `skip_features`.
  This is based on the features seen by a target, not the active features of the CC toolchain which option `skip_toolchain_features` is based on.

## [1.1.1](https://github.com/martis42/depend_on_what_you_use/releases/tag/1.1.1) - 2026.08.11

Broken release.
Next valid release is [1.1.2](#1.1.2).

## [1.1.0](https://github.com/martis42/depend_on_what_you_use/releases/tag/1.1.0) - 2026.08.10

Broken release.
Next valid release is [1.1.2](#1.1.2).

## [1.0.0](https://github.com/martis42/depend_on_what_you_use/releases/tag/1.0.0) - 2026.06.14

### BREAKING

- The legacy Bazel `WORKSPACE` dependency management system is no longer supported.
- Minimum Bazel version is now 7.6.0.
- Change paths and names of public DWYU symbols.
  This is done to have all targets under a common directory and to potentially support other languages besides C++ in the future.
  - `load("@depend_on_what_you_use//:defs.bzl", <symbol>)` changed to `load("@depend_on_what_you_use//dwyu/cc:defs.bzl", <symbol>)`.
  - The DWYU aspect factory function was renamed from `dwyu_aspect_factory` to `dwyu_cc_aspect_factory`.
    Meaning, load statement `load("@depend_on_what_you_use//:defs.bzl", "dwyu_aspect_factory")` changed to `load("@depend_on_what_you_use//dwyu/cc:defs.bzl", "dwyu_cc_aspect_factory")`.
  - The target for executing the apply_fixes script changes from `@depend_on_what_you_use//:apply_fixes` to `@depend_on_what_you_use//dwyu/apply_fixes:apply_fixes`.
- [apply_fixes] Reduce the API surface for discovering DWYU report files:
  - By default use the `bazel info` command to deduce the bazel-bin dir to search DWYU report files there.
  - Remove the logic to follow the convenience symlinks, as it was mostly redundant to using bazel info.
  - Rename script option `--search-path` to `--reports-search-path`.

### Removed

- [aspect] Remove the deprecated `no_preprocessor` option.
  Use option `preprocessing_mode = "fast"` instead, which behaves the same.

### Added

- [apply_fixes] No longer requires a host buildozer.
  DWYU now brings its own buildozer binary.
  Telling the tool to use a custom buildozer is still possible.

## [0.16.0](https://github.com/martis42/depend_on_what_you_use/releases/tag/0.16.0) - 2026.05.14

### Removed

- [aspect] Remove the deprecated options `experimental_set_cplusplus` and `use_cpp_implementation`.

### Deprecated

- [aspect] Deprecate the option `no_preprocessor` in favor of `preprocessing_mode`.
  To replace `no_preprocessor`, use `preprocessing_mode = "fast"`.

### Changed

- [aspect] Remove `extra_ignore_include_paths` from the `ignored_includes` option.
  There is no longer a default list of ignored includes, so extending a default list is no longer a use case.
  If you used `extra_ignore_include_paths`, simply add the same values to `ignore_include_paths`, which has now the same behavior.

### Fixed

- [aspect] Fix analysis for a genrule outputting multiple files.
- [aspect] Fix analysis when the same file is both in `hdrs` and `srcs`.
- [aspect] Prevent too long file names for DWYU output files.
- [apply_fixes] Fail with a clear error on missing buildozer.

### Added

- [aspect] Allow skipping the DWYU analysis based on active or inactive CC toolchain features with the new option `skip_toolchain_features`.
  For example, do not run DWYU if `layering_check` is disabled.
- [aspect] Offer a preprocessing mode ignoring system includes.
  For projects with conditional include statements only relying on macros and build settings from within the own stack, this can be a significant performance improvement.
  Activate this preprocessing mode via option `preprocessing_mode = "ignore_system_includes"`.

## [0.15.0](https://github.com/martis42/depend_on_what_you_use/releases/tag/0.15.0) - 2026.04.05

### Removed

- [aspect] Remove the legacy Python based aspect implementation.

### Added

- [apply_fixes] More robust logic to discover missing direct dependencies when applying fixes.

## [0.14.0](https://github.com/martis42/depend_on_what_you_use/releases/tag/0.14.0) - 2026.03.27

- Minimum required Python version is now 3.10.

### Removed

- [aspect] Remove the deprecated options `ignore_cc_toolchain_headers` and `cc_toolchain_headers_info`.
  They have no meaning for the C++ based implementation and were never enabled by default for the legacy Python implementation.
- [aspect] Remove the deprecated `use_implementation_deps` option.
  Use `analysis_optimizes_impl_deps` instead, which has the same behavior.
- [aspect] Remove the deprecated `experimental_no_preprocessor` option.
  Use `no_preprocessor` instead, which does the same.

### Fixed

- [apply_fixes] No longer suggest missing dependencies which are not visible to the target under inspection.

## [0.13.0](https://github.com/martis42/depend_on_what_you_use/releases/tag/0.13.0) - 2026.02.14

### Deprecated

- [aspect] Deprecate the option `use_implementation_deps`.
  Use instead option `analysis_optimizes_impl_deps`.
- [aspect] Deprecate the legacy feature `ignore_cc_toolchain_headers`.

### Changed

- Clarify that Linux is the main supported platform.
  MacOS and Windows are supported on a best effort basis.
- [aspect] **The new C++ based implementation is now the default implementation**.
  Fixes and improvements are from now on only done for the C++ implementation.
- [aspect] The recursive mode now always follows `implementation_deps`.

### Fixed

- [aspect] Fix action clashes for files with the same basename.
- [aspect] Fix a bug for including header files with the same name as the parent directory.
- [aspect] Includes discovery in "_no preprocessor_" mode now properly distinguishes between quote and system includes.
- [apply_fixes] Fix running the tool on Windows.

### Added

- [aspect] Allow using `--aspects_parameters` for the aspect options `analysis_optimizes_impl_deps` and `verbose`.
- [aspect] Allow toggling the individual DWYU checks for "_reporting missing direct deps_" and "_report unused deps_" separately.
  This only works with the new C++ based implementation.

## [0.12.0](https://github.com/martis42/depend_on_what_you_use/releases/tag/0.12.0) - 2026.01.05

### BREAKING

- Minimum Bazel version is now 7.2.1.

### Deprecated

- [aspect] Deducing the CC toolchain headers is deprecated.
  The options `ignore_cc_toolchain_headers` and `cc_toolchain_headers_info` are now deprecated.
- [aspect] Deprecate the option `experimental_no_preprocessor` in favor of `no_preprocessor`.

### Changed

- [aspect] Option `experimental_set_cplusplus` no longer guesses the `__cplusplus` value if it cannot be deduced from the `-std` compiler option.
  In this case, set it manually, e.g. via `-cxxopt`.
  Please note, setting `__cplusplus` whenever possible is a default feature of the new C++ based implementation.
- [aspect] Stabilize the `no_preprocessor` feature.
  We commit to offering a preprocessing mode in which the source files are parsed without considering conditional includes without using a real preprocessor.

### Added

- [aspect] The new C++ based implementation of the aspect is now finished.
  Use it with the option `use_cpp_implementation`.

## [0.11.0](https://github.com/martis42/depend_on_what_you_use/releases/tag/0.11.0) - 2025.11.30

### Deprecated

- [aspect] Deprecate option `experimental_set_cplusplus`.

### Fixed

- [aspect] Fix handling of `implementation_deps` pointing to external targets or targets manipulating their include paths.

### Added

- [aspect] Migrate more of the aspect logic to the new C++ based implementation, which is now able to preprocess the code.
  To test the partly migrated C++ based implementation use the option `use_cpp_implementation`.

## [0.10.0](https://github.com/martis42/depend_on_what_you_use/releases/tag/0.10.0) - 2025.09.13

### BREAKING

- Minimum required Python version is now 3.8.

### Fixed

- [apply_fixes] No longer crash on targets without deps.
- [aspect] Allow choosing a custom name other than `@depend_on_what_you_use` when using DWYU in your stack.

### Added

- [aspect] Enable automatically discovering the header files provided by the CC toolchain, which are then ignored during the DWYU analysis.
  To test this approach use option `ignore_cc_toolchain_headers=True`.
- [aspect] Start working on a new implementation based on C++ instead of Python.
  To use the partly C++ based implementation, set the option `use_cpp_implementation=True`.

## [0.9.0](https://github.com/martis42/depend_on_what_you_use/releases/tag/0.9.0) - 2025.05.30

### Changed

- [aspect] Improve performance while comparing include statements to headers provided by dependencies.

### Added

- [aspect] Allow disabling the preprocessor with the new option `experimental_no_preprocessor`.
  For projects without manipulation of include statements on preprocessor level, this can significantly reduce the time required for the DWYU analysis (up to factor 100 in benchmarks).

## [0.8.0](https://github.com/martis42/depend_on_what_you_use/releases/tag/0.8.0) - 2025.03.16

### Fixed

- [target_mapping] Ignore non C/C++ deps in in creating mappings.

## [0.7.0](https://github.com/martis42/depend_on_what_you_use/releases/tag/0.7.0) - 2025.02.01

### BREAKING

- Minimum Bazel version is now 6.4.0.

## [0.6.0](https://github.com/martis42/depend_on_what_you_use/releases/tag/0.6.0) - 2024.12.20

### BREAKING

- Minimum Bazel version is now 6.0.0.

### Fixed

- [aspect] Allow multiple dependencies providing the same header.
- [aspect] Fix recursion error in preprocessing.

### Added

- [aspect] Support workspaces using Bazel option `--noexperimental_python_import_all_repositories`.
- [aspect] Support Bazel CC toolchain feature `external_include_paths`.

## [0.5.0](https://github.com/martis42/depend_on_what_you_use/releases/tag/0.5.0) - 2024.09.07

### Fixed

- [aspect] Do not fail on targets with large list based attributes, which otherwise would fail due to the system's command length limit.
- [apply_fixes] Prevent failing while analyzing targets with empty hdrs attribute.

### Added

- [aspect] Experimental support for setting the `__cplusplus` macro to enable correctly processing files with preprocessor statements relying on this macro.
  Activate this via option `experimental_set_cplusplus`.

## [0.4.0](https://github.com/martis42/depend_on_what_you_use/releases/tag/0.4.0) - 2024.06.20

### Fixed

- [aspect] Add missing headers to C++ standard headers list.

## [0.3.0](https://github.com/martis42/depend_on_what_you_use/releases/tag/0.3.0) - 2024.05.26

### Changed

- [aspect] Extend and update C++ standard headers list.

### Fixed

- [aspect] Fix bug for analyzing `implementation_deps` when using target mappings.

### Changed

- [apply_fixes] Change how arguments are forwarded to buildozer.
  This is done to achieve a consistent API to how arguments are forwarded to the bazel commands.

### Added

- [apply_fixes] Support `cquery` to find missing dependencies.
- [apply_fixes] Allow forwarding arguments to the bazel commands which are executed by the apply_fixes script.
- [apply_fixes] Add a new method for discovering DWYU report files which should be more efficient for large workspaces.
  This is based on creating an execution log for the analysis done by the DWYU aspect and then forwarding this log to the apply_fixes script via `--dwyu-log-file`.

## [0.2.0](https://github.com/martis42/depend_on_what_you_use/releases/tag/0.2.0) - 2024.04.22

### Changed

- [apply_fixes] Improve dependency discovery heuristic.

### Added

- [aspect] Allow skipping external targets.

## [0.1.0](https://github.com/martis42/depend_on_what_you_use/releases/tag/0.1.0) - 2024.02.25

### BREAKING

- Minimum Bazel version is now 5.4.0.

### Changed

- [aspect] The output group has been renamed.
  Replace `--output_groups=cc_dwyu_output` with `--output_groups=dwyu` in your DWYU commands.
- [aspect] The name for the option to provide a config file for ignored include paths changed from `config = "//<your_config_file>.json"` to `ignored_includes = "//<your_config_file>.json"`.
- [apply_fixes] Rename the `--bazel-bin` apply_fixes CLI option to `--search-path` to make it more obvious how flexibly it can be used.

### Added

- Support `bzlmod`.
- [aspect] Allow specifying custom tags to skip DWYU analysis.
- [aspect] Add verbosity option `verbose` for debugging.

## [0.0.13](https://github.com/martis42/depend_on_what_you_use/releases/tag/0.0.13) - 2023.11.01

### Fixed

- [aspect] Fix recursive behavior for `implementation_deps`.

### Added

- [target_mapping] Add target mapping to allow virtually changing which targets provide which header.
  Use this to teach DWYU about targets forwarding headers.

## [0.0.12](https://github.com/martis42/depend_on_what_you_use/releases/tag/0.0.12) - 2023.10.18

### Fixed

- [aspect] Fix issue with long path names.

## [0.0.11](https://github.com/martis42/depend_on_what_you_use/releases/tag/0.0.11) - 2023.09.19

### BREAKING

- [aspect] Rework the include path analysis logic.
  Instead of inferring things based on custom heuristics we now rely more on what `CcInfo` provides.

### Added

- [aspect] Support relative include statements for virtual paths.
- [aspect] Enable processing defines from included headers.
- [aspect] Enable parsing of preprocessor tokens as include path.

## [0.0.10](https://github.com/martis42/depend_on_what_you_use/releases/tag/0.0.10) - 2023.07.30

### BREAKING

- Minimum Bazel version is now 5.0.0.

### Added

- [aspect] Support targets utilizing TreeArtifacts.
- [aspect] Enable using the `no-dwyu` tag to skip DWYU checks on specific targets.

## [0.0.9](https://github.com/martis42/depend_on_what_you_use/releases/tag/0.0.9) - 2023.04.29

### Added

- [aspect] Use preprocessor library `pcpp` to analyze code of targets under inspection.
- [aspect] Extract macro definitions from compiler flags and use them to properly resolve conditional includes.

## [0.0.8](https://github.com/martis42/depend_on_what_you_use/releases/tag/0.0.8) - 2023.03.17

### Added

- [apply_fixes] Support adding missing direct dependencies.
- [apply_fixes] Allow selecting which error categories are automatically fixed.

## [0.0.7](https://github.com/martis42/depend_on_what_you_use/releases/tag/0.0.7) - 2023.02.19

### Fixed

- [aspect] Fix regression for relative includes to own private headers.

## [0.0.6](https://github.com/martis42/depend_on_what_you_use/releases/tag/0.0.6) - 2023.02.04

### Changed

- [aspect] Rewrite logic for resolving relative include statements to make all header file system paths available to DWYU.
- [aspect] Improve support for resolving relative include statements.

### Fixed

- [aspect] Make sure the `implementation_deps` logic is not used on non library targets.
- [aspect] Use `re.match(pattern, include)` instead of `re.search(pattern, include)` for ignored include patterns to prevent pattern `a/.*` matching against include path `baz/a/b.h`.

### Added

- [aspect] Automatically skip analysis of targets where neither public-files nor private-files are present.

## [0.0.5](https://github.com/martis42/depend_on_what_you_use/releases/tag/0.0.5) - 2022.12.05

### BREAKING

- [aspect] Having an empty `ignore_include_paths` field in the config file is interpreted as "_no default ignores_" instead of "_use default ignores_".

### Changed

- [aspect] The various fields of the ignore includes config file are now optional.
- [aspect] There are now separate fields for to be ignored include paths and to be ignored patterns in the ignore includes config file.

## [0.0.4](https://github.com/martis42/depend_on_what_you_use/releases/tag/0.0.4) - 2022.11.02

### Added

- [apply_fixes] Support removing unused `implementation_deps`.
- [apply_fixes] Offer automatic fixes for public deps which should be private.
- [apply_fixes] Allow setting custom arguments for buildozer.

## [0.0.3](https://github.com/martis42/depend_on_what_you_use/releases/tag/0.0.3) - 2022.10.04

### BREAKING

- [aspect] Drop support for `interface_deps`.
  This feature has been removed again from Bazel 6.

## [0.0.2](https://github.com/martis42/depend_on_what_you_use/releases/tag/0.0.2) - 2022.07.11

### BREAKING

- [apply_fixes] New CLI interface for the apply_fixes script:
  - Automatically detect the workspace root if no workspace is specified.
  - Allow using the convenience symlinks to find the bazel-bin dir.
    This is now the default behavior.
    Utilizing bazel info command to find the bazel-bin directory can be chosen via an opt-in.
  - If using bazel info to to discover the bazel-bin directory, one can choose the compilation mode.
  - Allow providing the bazel-bin directory directly.
  - Fail if no DWYU report files can be discovered.

### Added

- [aspect] Support Bazel 6 `interface_deps`.
- [aspect] Allow ignoring include statements with regex patterns.
- [apply_fixes] Warn if a fix could not be performed and provides hints about possible problems.

## [0.0.1](https://github.com/martis42/depend_on_what_you_use/releases/tag/0.0.1) - 2022.04.28

First proper release starting the public history.
