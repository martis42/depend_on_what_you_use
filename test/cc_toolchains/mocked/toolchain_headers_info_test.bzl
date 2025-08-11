load("@depend_on_what_you_use//dwyu/cc_toolchain_headers:providers.bzl", "DwyuCcToolchainHeadersInfo")

def _toolchain_headers_info_test_impl(ctx):
    # Distinguish between hermetic toolchain and system toolchain
    if ctx.attr._test_tool[PyRuntimeInfo].interpreter:
        python = ctx.attr._test_tool[PyRuntimeInfo].interpreter.short_path
    else:
        python = ctx.attr._test_tool[PyRuntimeInfo].interpreter_path

    executable_tpl = "{PYTHON} {TEST} --input {INPUT} --expected_header_files {EXPECTED_FILES} --expected_include_statements {EXPECTED_INCLUDES}\n"
    executable_content = executable_tpl.format(
        PYTHON = python,
        TEST = ctx.attr._test_tool[DefaultInfo].files_to_run.executable.short_path,
        INPUT = ctx.file.headers_info.short_path,
        EXPECTED_FILES = " ".join(ctx.attr.expected_header_files),
        EXPECTED_INCLUDES = " ".join(ctx.attr.expected_include_statements),
    )

    executable = ctx.actions.declare_file("{}.sh".format(ctx.label.name))
    ctx.actions.write(executable, executable_content, is_executable = True)

    return DefaultInfo(
        executable = executable,
        runfiles = ctx.runfiles(files = [ctx.file.headers_info], transitive_files = ctx.attr._test_tool[DefaultInfo].default_runfiles.files),
    )

def _rule_factory(toolchain_transition):
    return rule(
        implementation = _toolchain_headers_info_test_impl,
        attrs = {
            "expected_header_files": attr.string_list(mandatory = True, doc = "Headers files we expect to discover in the toolchain"),
            "expected_include_statements": attr.string_list(mandatory = True, doc = "Possible include statements to header files we expect to discover in the toolchain"),
            "headers_info": attr.label(
                allow_single_file = True,
                providers = [DwyuCcToolchainHeadersInfo],
                cfg = toolchain_transition,
                doc = "Toolchain header information we compare to the expected headers",
            ),
            "_test_tool": attr.label(default = Label("//tools:toolchain_headers_info_check"), executable = True, cfg = "exec"),
        },
        test = True,
    )

def _transition_factory(impl):
    return transition(
        implementation = impl,
        inputs = [],
        outputs = ["//command_line_option:extra_toolchains"],
    )

def _classic_gcc_like_transition_impl(settings, attr):
    # buildifier: disable=unused-variable
    _ignore = (settings, attr)
    return {"//command_line_option:extra_toolchains": "@test_toolchain_classic//:gcc_like_toolchain"}

def _classic_msvc_like_transition_impl(settings, attr):
    # buildifier: disable=unused-variable
    _ignore = (settings, attr)
    return {"//command_line_option:extra_toolchains": "@test_toolchain_classic//:msvc_like_toolchain"}

def _classic_unknown_with_built_in_dirs_transition_impl(settings, attr):
    # buildifier: disable=unused-variable
    _ignore = (settings, attr)
    return {"//command_line_option:extra_toolchains": "@test_toolchain_classic//:unknown_with_built_in_dirs_toolchain"}

def _rule_based_gcc_like_transition_impl(settings, attr):
    # buildifier: disable=unused-variable
    _ignore = (settings, attr)
    return {"//command_line_option:extra_toolchains": "@test_toolchain_rule_based//:gcc_like_toolchain"}

def _rule_based_msvc_like_transition_impl(settings, attr):
    # buildifier: disable=unused-variable
    _ignore = (settings, attr)
    return {"//command_line_option:extra_toolchains": "@test_toolchain_rule_based//:msvc_like_toolchain"}

classic_gcc_like_headers_info_test = _rule_factory(_transition_factory(_classic_gcc_like_transition_impl))
classic_msvc_like_headers_info_test = _rule_factory(_transition_factory(_classic_msvc_like_transition_impl))
classic_unknown_with_built_in_dirs_headers_info_test = _rule_factory(_transition_factory(_classic_unknown_with_built_in_dirs_transition_impl))
rule_based_gcc_like_headers_info_test = _rule_factory(_transition_factory(_rule_based_gcc_like_transition_impl))
rule_based_msvc_like_headers_info_test = _rule_factory(_transition_factory(_rule_based_msvc_like_transition_impl))

# _RULES_MAP = {
#     "classic_gcc_like": _classic_gcc_like_test,
#     "classic_msvc_like": _classic_msvc_like_test,
#     "classic_unknown_with_built_in_dirs": _classic_unknown_with_built_in_dirs_test,
#     "rule_based_gcc_like": _rule_based_gcc_like_test,
#     "rule_based_msvc_like": _rule_based_msvc_like_test,
# }

# def toolchain_headers_info_tests(headers_info, expected_header_files, expected_include_statements, **kwargs):
#     for id, rule in _RULES_MAP.items():
#         rule(
#             name = "{}_test".format(id),
#             headers_info = headers_info,
#             expected_header_files = expected_header_files,
#             expected_include_statements = expected_include_statements,
#             **kwargs
#         )
