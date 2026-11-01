load("@rules_cc//cc/common:cc_info.bzl", "CcInfo")
load(":common.bzl", "DwyuDirectDepsCcInfo", "create_remapped_cc_info", "filter_compilation_contexts")
load(":providers.bzl", "DwyuRemappedCcInfo")

visibility("//dwyu/cc/cc_info_mapping/...")

def _aggregate_direct_deps_aspect_impl(_, ctx):
    """
    We deliberately ignore implementation_deps since headers provided by them shall by design not be used by consumers
    of the target.
    """

    # 'cc_*' targets can depend on things like sh_library not providing CcInfo
    dep_compilation_contexts = {
        dep.label: dep[CcInfo].compilation_context
        for dep in ctx.rule.attr.deps
        if CcInfo in dep
    }

    return DwyuDirectDepsCcInfo(deps_to_compilation_context = dep_compilation_contexts)

_aggregate_direct_deps_aspect = aspect(
    implementation = _aggregate_direct_deps_aspect_impl,
    provides = [DwyuDirectDepsCcInfo],
    attr_aspects = [],
)

def _mapping_to_direct_deps_impl(ctx):
    return create_remapped_cc_info(
        target = ctx.attr.target,
        mapped_compilation_contexts = filter_compilation_contexts(
            deps_to_compilation_context = ctx.attr.target[DwyuDirectDepsCcInfo].deps_to_compilation_context,
            label_filter = ctx.attr.filter,
        ),
    )

mapping_to_direct_deps = rule(
    implementation = _mapping_to_direct_deps_impl,
    provides = [DwyuRemappedCcInfo],
    attrs = {
        "filter": attr.string_list(doc = "List of canonical target names of the targets which shall be mapped"),
        "target": attr.label(aspects = [_aggregate_direct_deps_aspect], providers = [CcInfo]),
    },
    doc = """
Make headers from direct dependencies available as if they where provided by the main target itself.
We do so by merging the compilation_context information from the direct dependencies into the main target's CcInfo.
We explicitly ignore implementation_deps, as allowing to map them would break their design of not being visible to users of the target.

By default map all direct dependencies.
If the `filter` attribute is provided, only map direct dependencies matching the canonical target names from the `filter` attribute.
""",
)
