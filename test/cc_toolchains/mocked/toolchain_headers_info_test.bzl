load("@depend_on_what_you_use//src/toolchain_headers:providers.bzl", "DwyuCcToolchainHeadersInfo")

def _toolchain_headers_info_test_impl(ctx):
    # Distinguish between hermetic toolchain and system toolchain
    if ctx.attr._test_tool[PyRuntimeInfo].interpreter:
        python = ctx.attr._test_tool[PyRuntimeInfo].interpreter.short_path
    else:
        python = ctx.attr._test_tool[PyRuntimeInfo].interpreter_path

    executable_tpl = "{PYTHON} {TEST} --input {INPUT} --expected_headers {EXPECTED}\n"
    executable_content = executable_tpl.format(
        PYTHON = python,
        TEST = ctx.attr._test_tool[DefaultInfo].files_to_run.executable.short_path,
        INPUT = ctx.file.headers_info.short_path,
        EXPECTED = " ".join(ctx.attr.expected_headers),
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
            "expected_headers": attr.string_list(mandatory = True, doc = "Headers which we expect to be discovered by the toolchain"),
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

def _toolchain_classic_transition_impl(settings, attr):
    # buildifier: disable=unused-variable
    _ignore = (settings, attr)
    return {"//command_line_option:extra_toolchains": "@test_toolchain_classic//:toolchain"}

def _toolchain_classic_gcc_like_transition_impl(settings, attr):
    # buildifier: disable=unused-variable
    _ignore = (settings, attr)
    return {"//command_line_option:extra_toolchains": "@test_toolchain_classic//:gcc_like_toolchain"}

def _toolchain_classic_msvc_like_transition_impl(settings, attr):
    # buildifier: disable=unused-variable
    _ignore = (settings, attr)
    return {"//command_line_option:extra_toolchains": "@test_toolchain_classic//:msvc_like_toolchain"}

def _toolchain_rule_based_transition_impl(settings, attr):
    # buildifier: disable=unused-variable
    _ignore = (settings, attr)
    return {"//command_line_option:extra_toolchains": "@test_toolchain_rule_based//:toolchain"}

_toolchain_classic_test = _rule_factory(_transition_factory(_toolchain_classic_transition_impl))
_toolchain_classic_gcc_like_test = _rule_factory(_transition_factory(_toolchain_classic_gcc_like_transition_impl))
_toolchain_classic_msvc_like_test = _rule_factory(_transition_factory(_toolchain_classic_msvc_like_transition_impl))
_toolchain_rule_based_test = _rule_factory(_transition_factory(_toolchain_rule_based_transition_impl))

_RULES_MAP = {
    "@test_toolchain_classic//:gcc_like_toolchain": _toolchain_classic_gcc_like_test,
    "@test_toolchain_classic//:msvc_like_toolchain": _toolchain_classic_msvc_like_test,
    "@test_toolchain_classic//:toolchain": _toolchain_classic_test,
    "@test_toolchain_rule_based//:toolchain": _toolchain_rule_based_test,
}

def toolchain_headers_info_test(name, headers_info, toolchain, **kwargs):
    test_rule = _RULES_MAP[toolchain]
    test_rule(
        name = name,
        headers_info = headers_info,
        **kwargs
    )
