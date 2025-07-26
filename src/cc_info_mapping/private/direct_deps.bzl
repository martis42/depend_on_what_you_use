load("@rules_cc//cc/common:cc_common.bzl", "cc_common")
load("@rules_cc//cc/common:cc_info.bzl", "CcInfo")
load(":providers.bzl", "DwyuRemappedCcInfo")

visibility("//src/cc_info_mapping/...")

def _aggregate_direct_deps_aspect_impl(target, ctx):
    """
    We deliberately ignore implementation_deps since headers provided by them shall by design not be used by consumers
    of the target.
    """

    # 'cc_*' targets can depend on things like sh_library not providing CcInfo
    cc_targets = [target] + [dep for dep in ctx.rule.attr.deps if CcInfo in dep]
    aggregated_compilation_context = cc_common.merge_compilation_contexts(
        compilation_contexts = [tgt[CcInfo].compilation_context for tgt in cc_targets],
    )

    return DwyuRemappedCcInfo(target = target.label, cc_info = CcInfo(
        compilation_context = aggregated_compilation_context,
        linking_context = target[CcInfo].linking_context,
    ))

_aggregate_direct_deps_aspect = aspect(
    implementation = _aggregate_direct_deps_aspect_impl,
    provides = [DwyuRemappedCcInfo],
    attr_aspects = [],
)

def _mapping_to_direct_deps_impl(ctx):
    return ctx.attr.target[DwyuRemappedCcInfo]

mapping_to_direct_deps = rule(
    implementation = _mapping_to_direct_deps_impl,
    provides = [DwyuRemappedCcInfo],
    attrs = {
        "target": attr.label(aspects = [_aggregate_direct_deps_aspect], providers = [CcInfo]),
    },
    doc = """
Make headers from all direct dependencies available as if they where provided by the main target itself.
We do so by merging the compilation_context information from the direct dependencies into the main target's CcInfo.
We explicitly ignore implementation_deps, as allowing to map them would break their design of not being visible to users of the target.
    """,
)
