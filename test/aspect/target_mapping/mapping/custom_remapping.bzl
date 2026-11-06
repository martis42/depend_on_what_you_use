load("@depend_on_what_you_use//dwyu/cc/cc_info_mapping:providers.bzl", "DwyuRemappedCcInfo")
load("@rules_cc//cc/common:cc_common.bzl", "cc_common")
load("@rules_cc//cc/common:cc_info.bzl", "CcInfo")

def _custom_remapping_impl(ctx):
    original = ctx.attr.target[CcInfo]
    contexts = [original.compilation_context] + [
        dep[CcInfo].compilation_context
        for dep in ctx.attr.selected_deps
    ]
    return [DwyuRemappedCcInfo(
        target = ctx.attr.target.label,
        cc_info = CcInfo(
            compilation_context = cc_common.merge_compilation_contexts(compilation_contexts = contexts),
            linking_context = original.linking_context,
        ),
    )]

custom_remapping = rule(
    implementation = _custom_remapping_impl,
    attrs = {
        "selected_deps": attr.label_list(providers = [CcInfo], doc = "List of dependencies to be mapped into the target"),
        "target": attr.label(mandatory = True, providers = [CcInfo], doc = "Target to be remapped"),
    },
    provides = [DwyuRemappedCcInfo],
)
