load("@rules_cc//cc/common:cc_common.bzl", "cc_common")
load("@rules_cc//cc/common:cc_info.bzl", "CcInfo")
load(":providers.bzl", "DwyuCcInfoRemapInfo")

def _aggregate_transitive_deps_aspect_impl(target, ctx):
    all_cc_info = [target[CcInfo]]
    all_cc_info.extend([dep[DwyuCcInfoRemapInfo].cc_info for dep in ctx.rule.attr.deps])
    aggregated_compilation_context = cc_common.merge_compilation_contexts(
        compilation_contexts = [cci.compilation_context for cci in all_cc_info],
    )

    return DwyuCcInfoRemapInfo(target = target.label, cc_info = CcInfo(
        compilation_context = aggregated_compilation_context,
        linking_context = target[CcInfo].linking_context,
    ))

_aggregate_transitive_deps_aspect = aspect(
    implementation = _aggregate_transitive_deps_aspect_impl,
    provides = [DwyuCcInfoRemapInfo],
    attr_aspects = ["deps"],
)

def _mapping_to_transitive_deps_impl(ctx):
    return ctx.attr.target[DwyuCcInfoRemapInfo]

mapping_to_transitive_deps = rule(
    implementation = _mapping_to_transitive_deps_impl,
    provides = [DwyuCcInfoRemapInfo],
    attrs = {
        "target": attr.label(aspects = [_aggregate_transitive_deps_aspect], providers = [CcInfo]),
    },
    doc = """
Make headers from all transitive dependencies available as if they where provided by the main target itself.
We do so by recursively merging the compilation_context information from the dependencies into the main target's CcInfo.
We explicitly ignore implementation_deps, as allowing to map them would break their design of not being visible to users of the target.
    """,
)
