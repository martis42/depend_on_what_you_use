load("@rules_cc//cc/common:cc_common.bzl", "cc_common")
load("@rules_cc//cc/common:cc_info.bzl", "CcInfo")

def _custom_lib_impl(ctx):
    return [
        cc_common.merge_cc_infos(cc_infos = [dep[CcInfo] for dep in ctx.attr.custom_deps]),
    ]

custom_lib = rule(
    implementation = _custom_lib_impl,
    attrs = {
        "custom_deps": attr.label_list(providers = [CcInfo]),
    },
    provides = [CcInfo],
    doc = "Minimal custom rule forwarding the CcInfo of its dependencies with custom rule attributes.",
)
