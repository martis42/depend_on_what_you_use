load("@rules_cc//cc/common:cc_common.bzl", "cc_common")
load("@rules_cc//cc/common:cc_info.bzl", "CcInfo")
load("//dwyu/cc/cc_info_mapping:providers.bzl", "DwyuRemappedCcInfo")

def _custom_remapping_impl(ctx):
    original = ctx.attr.target[CcInfo]
    return [DwyuRemappedCcInfo(
        target = ctx.attr.target.label,
        cc_info = CcInfo(
            compilation_context = cc_common.merge_compilation_contexts(compilation_contexts = [
                original.compilation_context,
                ctx.attr.dep[CcInfo].compilation_context,
            ]),
            linking_context = original.linking_context,
        ),
    )]

custom_remapping = rule(
    implementation = _custom_remapping_impl,
    attrs = {
        "dep": attr.label(mandatory = True, providers = [CcInfo]),
        "target": attr.label(mandatory = True, providers = [CcInfo]),
    },
    provides = [DwyuRemappedCcInfo],
)

def _invalid_remapping_impl(ctx):
    return [DwyuRemappedCcInfo(
        target = ctx.attr.invalid_target if ctx.attr.invalid_target else ctx.label,
        cc_info = ctx.attr.invalid_cc_info if ctx.attr.invalid_cc_info else CcInfo(),
    )]

invalid_remapping = rule(
    implementation = _invalid_remapping_impl,
    attrs = {
        "invalid_cc_info": attr.string(),
        "invalid_target": attr.string(),
    },
    provides = [DwyuRemappedCcInfo],
)
