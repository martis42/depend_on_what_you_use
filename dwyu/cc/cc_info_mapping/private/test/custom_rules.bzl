load("@rules_cc//cc/common:cc_common.bzl", "cc_common")
load("@rules_cc//cc/common:cc_info.bzl", "CcInfo")

visibility("//dwyu/cc/cc_info_mapping/...")

def _cc_info_with_custom_deps_impl(ctx):
    compilation_contexts = [cc_common.create_compilation_context(
        headers = depset(ctx.files.hdrs),
    )]
    if ctx.attr.single_dep:
        compilation_contexts.append(ctx.attr.single_dep[CcInfo].compilation_context)
    compilation_contexts += [
        dependency[CcInfo].compilation_context
        for dependency in ctx.attr.multiple_deps
    ]
    return [CcInfo(compilation_context = cc_common.merge_compilation_contexts(
        compilation_contexts = compilation_contexts,
    ))]

# Minimal custom rule that provides CcInfo and depends on other CC targets, but deliberately has no "deps" attribute
cc_info_with_custom_deps = rule(
    implementation = _cc_info_with_custom_deps_impl,
    provides = [CcInfo],
    attrs = {
        "hdrs": attr.label_list(allow_files = [".h"]),
        "multiple_deps": attr.label_list(providers = [CcInfo]),
        "non_target_attr": attr.string(),
        "non_target_list_attr": attr.string_list(),
        "single_dep": attr.label(providers = [CcInfo]),
    },
)
