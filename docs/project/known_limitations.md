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

There are also preprocessor constructs our preprocessing cannot evaluate at all, since they are not part of the C++11 standard our preprocessing implements.
Examples are `__has_include` or invoking a variadic macro without arguments for the variadic part.
When preprocessing a file hits such a construct, DWYU automatically falls back to lexically scanning that file for include statements, like `preprocessing_mode = "fast"` does.
Thereby, include statements are never silently dropped due to such constructs.
The trade-off is that for the affected files conditional include statements are over-reported, as the lexical scanning cannot evaluate the conditional logic around them.
If the aspect's `verbose` option is enabled, the preprocessing reports each file for which this fallback is used.

If your project is impacted by those edge cases, you can try some mitigation strategies:

- You can use the `preprocessing_mode = "fast"` DWYU aspect option to disable preprocessing.
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
