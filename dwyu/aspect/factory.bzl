load("@rules_cc//cc:find_cc_toolchain.bzl", "use_cc_toolchain")
load("//dwyu/cc_info_mapping:providers.bzl", "DwyuCcInfoMappingInfo")
load("//dwyu/cc_toolchain_headers:providers.bzl", "DwyuCcToolchainHeadersInfo")
load(":dwyu.bzl", "dwyu_aspect_impl")

_DEFAULT_SKIPPED_TAGS = ["no-dwyu"]

def dwyu_aspect_factory(
        experimental_no_preprocessor = False,
        experimental_set_cplusplus = False,
        ignore_cc_toolchain_headers = False,
        ignored_includes = None,
        recursive = False,
        skip_external_targets = False,
        skipped_tags = _DEFAULT_SKIPPED_TAGS,
        target_mapping = None,
        cc_toolchain_headers_info = None,
        use_cpp_implementation = False,
        use_implementation_deps = False,
        verbose = False):
    """
    Create a "**D**epend on **W**hat **Y**ou **U**se" (DWYU) aspect.

    Use the factory in a `.bzl` file to instantiate a DWYU aspect:
    ```starlark
    load("@depend_on_what_you_use//:defs.bzl", "dwyu_aspect_factory")

    your_dwyu_aspect = dwyu_aspect_factory(<aspect_options>)
    ```

    Args:
        experimental_no_preprocessor: **Experimental** feature whose behavior is not yet stable and might change at any time.<br>
                                      This option disables the preprocessing before discovering the include statements in the files under inspection.
                                      Do not use this option, unless you are sure you really need this performance boost and the downsides are not relevant to your project.
                                      When the preprocessing is disabled, DWYU still ignores commented include statements.<br>
                                      When using this option, DWYU will no longer be able to correctly resolve conditional include logic (`#ifdef` around include statements) or any other preprocessor directives and macros influencing include statements.
                                      A common example requiring preprocessing is having different include statements and Bazel target dependencies depending on whether the host is a Windows or Linux system.<br>
                                      By default, DWYU uses a preprocessor to resolve such cases.
                                      This preprocessor is however slow, when analyzing complex files.
                                      Using this option can speed up the DWYU analysis significantly.

        experimental_set_cplusplus: **DEPRECATED**: This feature will be removed in the next release.
                                    See the [define_macros](/examples/define_macros/) example for the forward path solution.<br><br>
                                    `__cplusplus` is a macro defined by the compiler specifying if C++ is used to compile the file and which C++ standard is used.<br>
                                    DWYU cannot treat this like other preprocessor defines, as this is often not coming from the command line or the Bazel C++ toolchain.
                                    The compiler itself defines the value for `__cplusplus` and sets it internally during preprocessing.<br>
                                    This option enables a heuristic to set `__cplusplus` for the preprocessor used internally by DWYU:
                                    <ul><li>
                                      If at least one source file is not using file extension [`.c`, `.h`], set `__cplusplus` to 1.
                                    </li><li>
                                      If a common compiler option is used to set the C++ standard with an unknown value, set `__cplusplus` to 1.
                                    </li><li>
                                      If a common compiler option is used to set the C++ standard with an known value, set `__cplusplus` according to [this map](https://en.cppreference.com/w/cpp/preprocessor/replace#Predefined_macros).
                                    </li></ul>
                                    This feature is demonstrated in the [set_cpp_standard example](/examples/set_cpp_standard).

        ignore_cc_toolchain_headers: Infer automatically which header files can be reached through the active CC toolchain without the target under inspection having to declare any explicit dependency.
                                     Include statements to those headers are ignored when DWYU compares include statements to the dependencies of the target under inspection.
                                     Automatically inferring the toolchain headers will become the default behavior in a future release.<br>
                                     If this option is false, the legacy DWYU behavior is to use a manually maintained list of system headers and standard library headers.
                                     This list of headers can be seen in [std_header.py](/dwyu/aspect/private/analyze_includes/std_header.py).<br>
                                     There is no reliable API available in Starlark to get all include paths to CC toolchain headers, since [CcToolchainInfo.built_in_include_directories](https://bazel.build/rules/lib/providers/CcToolchainInfo#built_in_include_directories) is an optional field without sanity checking.
                                     Thus, DWYU uses knowledge about the most common compilers and how to extract the include paths available to them.
                                     The supported compilers are GCC, clang and MSVC.
                                     A best effort fallback strategy exists for CC toolchain with unknown compilers specifying [CcToolchainInfo.built_in_include_directories](https://bazel.build/rules/lib/providers/CcToolchainInfo#built_in_include_directories).
                                     Consequently, there might be CC toolchains with which this feature does not work. In such a case you have multiple options:<br>
                                     <ul><li>
                                       Report a bug to DWYU if you believe your CC toolchain should be supported.
                                     </li><li>
                                       Use the [toolchain_headers_info](https://github.com/martis42/depend_on_what_you_use/blob/main/docs/dwyu_aspect.md#dwyu_aspect_factory-toolchain_headers_info) option to inject your own analysis of the CC toolchain.
                                     </li><li>
                                       Use the legacy behavior by setting this attribute to false.
                                     </li></ul>

        ignored_includes: By default, DWYU ignores all headers from the standard library when comparing include statements to the dependencies.
                          This list of headers can be seen in [std_header.py](/dwyu/aspect/private/analyze_includes/std_header.py).<br>
                          You can extend this list of ignored headers or replace it with a custom one by providing a json file with the information to this attribute.<br>
                          Specification of possible files in the json file:
                          <ul><li>
                            `ignore_include_paths` : List of include paths which are ignored by the analysis.
                            Setting this **disables ignoring the system and standard library include paths**.
                          </li><li>
                            `extra_ignore_include_paths` : List of concrete include paths which are ignored by the analysis.
                            Those are always ignored, no matter what other fields you provide.
                          </li><li>
                            `ignore_include_patterns` : List of patterns for include paths which are ignored by the analysis.
                            Patterns have to be compatible to Python [regex syntax](https://docs.python.org/3/library/re.html#regular-expression-syntax).
                            The [match](https://docs.python.org/3/library/re.html#re.match) function is used to process the patterns.
                          </li></ul>
                          This feature is demonstrated in the [ignoring_includes example](/examples/ignoring_includes).

        recursive: By default, the DWYU aspect analyzes only the target it is being applied to.
                   You can change this to recursively analyzing dependencies following the `deps` and `implementation_deps` attributes by setting this to True.<br>
                   This feature is demonstrated in the [recursion example](/examples/recursion).

        skip_external_targets: Sometimes external dependencies are not our under control and thus analyzing them is of little value.
                               If this flag is True, DWYU will automatically skip all targets from external workspaces.
                               This can be useful in combination with the recursive analysis mode.<br>
                               This feature is demonstrated in the [skipping_targets example](/examples/skipping_targets).

        skipped_tags: Do not execute the DWYU analysis on targets with at least one of those tags.
                      By default skips the analysis for targets tagged with 'no-dwyu'.<br>
                      This feature is demonstrated in the [skipping_targets example](/examples/skipping_targets).

        target_mapping: Accepts a [dwyu_make_cc_info_mapping](/docs/cc_info_mapping.md) target.
                        Allows virtually combining targets regarding which header can be provided by which dependency.
                        For the full details see the `dwyu_make_cc_info_mapping` documentation.<br>
                        This feature is demonstrated in the [target_mapping example](/examples/target_mapping).

        cc_toolchain_headers_info: Requires setting [ignore_cc_toolchain_headers](https://github.com/martis42/depend_on_what_you_use/blob/main/docs/dwyu_aspect.md#dwyu_aspect_factory-ignore_cc_toolchain_headers) to True.
                                   Use this option to inject your own analysis of the CC toolchain.
                                   Provide the label to a target offering the provider [DwyuCcToolchainHeadersInfo](/dwyu/cc_toolchain_headers/providers.bzl).
                                   It is your choice if you simply use a hard coded list or implement a logic looking up the information dynamically.
                                   Please note, the required information are not the include paths where the compiler looks for toolchain headers, but all the sub paths to header files relative to those include directories.
                                   In other words, a list of all possible include statements in your code which would point to CC toolchain headers.

        use_cpp_implementation: Switch parts of the internal tools executed by DWYU to a C++ based implementation instead of Python scripting.
                                This is mostly a performance improvement and DWYU should not behave significantly different.
                                That much said, different behavior in certain edge cases is possible.
                                For now only parts of the implementation are switched to C++.
                                We will migrate more parts of the implementation step by step in future releases.
                                Since, the C++ based implementation is new, this is for now an opt-in.
                                However, this will become the default eventually.

        use_implementation_deps: `cc_library` offers the attribute [`implementation_deps`](https://bazel.build/reference/be/c-cpp#cc_library.implementation_deps) to distinguish between public (aka interface) and private (aka implementation) dependencies.
                                 Headers from the private dependencies are not made available to users of the library.<br>
                                 Setting this to True allows DWYU to raise an error if headers from a `deps` dependency are used only in private files.
                                 In such a cease the dependency should be moved from `deps` to `implementation_deps`.<br>
                                 This feature is demonstrated in the [basic_usage example](/examples/basic_usage).

        verbose: If True, print debugging information about what DWYU does.

    Returns:
        Configured DWYU aspect
    """
    attr_aspects = []
    if recursive:
        attr_aspects = ["implementation_deps", "deps"] if use_implementation_deps else ["deps"]
    aspect_ignored_includes = [ignored_includes] if ignored_includes else []
    aspect_skipped_tags = _DEFAULT_SKIPPED_TAGS if skipped_tags == _DEFAULT_SKIPPED_TAGS else skipped_tags
    aspect_target_mapping = [target_mapping] if target_mapping else []
    if ignore_cc_toolchain_headers:
        cc_toolchain_headers = cc_toolchain_headers_info if cc_toolchain_headers_info else Label("//dwyu/aspect/private:cc_toolchain_headers")
    else:
        cc_toolchain_headers = Label("//dwyu/aspect/private:cc_toolchain_headers_stub")
    target_processor = Label("//dwyu/aspect/private/process_target:main_cc") if use_cpp_implementation else Label("//dwyu/aspect/private/process_target:main_py")
    return aspect(
        implementation = dwyu_aspect_impl,
        attr_aspects = attr_aspects,
        fragments = ["cpp"],
        # Uncomment when minimum Bazel version is 7.0.0, see https://github.com/bazelbuild/bazel/issues/19609
        # DWYU is only able to work on targets providing CcInfo. Other targets shall be skipped.
        # required_providers = [CcInfo],
        toolchains = use_cc_toolchain(mandatory = True),
        attrs = {
            # Remove after minimum Bazel version is 7, see https://docs.google.com/document/d/14vxMd3rTpzAwUI9ng1km1mp-7MrVeyGFnNbXKF_XhAM/edit?tab=t.0
            "_cc_toolchain": attr.label(default = Label("@rules_cc//cc:current_cc_toolchain")),
            "_cc_toolchain_headers": attr.label(
                default = cc_toolchain_headers,
                providers = [DwyuCcToolchainHeadersInfo],
            ),
            "_dwyu_binary": attr.label(
                default = Label("//dwyu/aspect/private/analyze_includes:analyze_includes"),
                allow_files = True,
                executable = True,
                cfg = "exec",
                doc = "Tool Analyzing the include statement in the source code under inspection" +
                      " and comparing them to the available dependencies.",
            ),
            "_ignore_cc_toolchain_headers": attr.bool(
                default = ignore_cc_toolchain_headers,
            ),
            "_ignored_includes": attr.label_list(
                default = aspect_ignored_includes,
                allow_files = [".json"],
            ),
            "_no_preprocessor": attr.bool(
                default = experimental_no_preprocessor,
            ),
            "_recursive": attr.bool(
                default = recursive,
            ),
            "_set_cplusplus": attr.bool(
                default = experimental_set_cplusplus,
            ),
            "_skip_external_targets": attr.bool(
                default = skip_external_targets,
            ),
            "_skipped_tags": attr.string_list(
                default = aspect_skipped_tags,
            ),
            "_target_mapping": attr.label_list(
                providers = [DwyuCcInfoMappingInfo],
                default = aspect_target_mapping,
            ),
            "_tool_analyze_preprocessing_results": attr.label(
                default = Label("//dwyu/aspect/private/analyze_preprocessor_results:main"),
                executable = True,
                cfg = "exec",
                doc = "Alternative for '_dwyu_binary' for comparing include statements to dependencies when using the C++ implementation with a dedicated preprocessing per source file under inspection.",
            ),
            "_tool_preprocessing": attr.label(
                default = Label("//dwyu/aspect/private/preprocessing:main"),
                executable = True,
                cfg = "exec",
                doc = "Preprocess the source code under inspection to resolve conditional preprocessor statements and discover include statements.",
            ),
            "_tool_process_target": attr.label(
                default = target_processor,
                executable = True,
                cfg = "exec",
                doc = "Tool for processing the target under inspection and its dependencies. We have to perform this" +
                      " as separate action, since otherwise we can't look into TreeArtifact sources.",
            ),
            "_use_cpp_implementation": attr.bool(
                default = use_cpp_implementation,
            ),
            "_use_implementation_deps": attr.bool(
                default = use_implementation_deps,
            ),
            "_verbose": attr.bool(
                default = verbose,
            ),
        },
    )
