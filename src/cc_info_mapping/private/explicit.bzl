load("@rules_cc//cc/common:cc_common.bzl", "cc_common")
load("@rules_cc//cc/common:cc_info.bzl", "CcInfo")
load(":providers.bzl", "DwyuRemappedCcInfo")

def _explicit_mapping_impl(ctx):
    aggregated_compilation_context = cc_common.merge_compilation_contexts(
        compilation_contexts =
            [tgt[CcInfo].compilation_context for tgt in [ctx.attr.target] + ctx.attr.map_to],
    )

    return DwyuRemappedCcInfo(target = ctx.attr.target.label, cc_info = CcInfo(
        compilation_context = aggregated_compilation_context,
        linking_context = ctx.attr.target[CcInfo].linking_context,
    ))

explicit_mapping = rule(
    implementation = _explicit_mapping_impl,
    provides = [DwyuRemappedCcInfo],
    attrs = {
        "map_to": attr.label_list(providers = [CcInfo]),
        "target": attr.label(providers = [CcInfo]),
    },
    doc = """
Make headers from all explicitly listed targets available as if they where provided by the main target itself.
We do so by merging the compilation_context information from the listed targets into the main target's CcInfo.
    """,
)
