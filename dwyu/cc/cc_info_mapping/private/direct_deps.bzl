load("@rules_cc//cc/common:cc_common.bzl", "cc_common")
load("@rules_cc//cc/common:cc_info.bzl", "CcInfo")
load(":providers.bzl", "DwyuRemappedCcInfo")

visibility("//dwyu/cc/cc_info_mapping/...")

_DwyuDirectDepsCcInfo = provider(
    "Compilation contexts of dependencies, to be filtered and merged by the rule using this aspect.",
    fields = {
        "deps_to_compilation_context": "Dictionary mapping the Label of a dependency to its CcInfo.compilation_context",
    },
)

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

    return _DwyuDirectDepsCcInfo(deps_to_compilation_context = dep_compilation_contexts)

_aggregate_direct_deps_aspect = aspect(
    implementation = _aggregate_direct_deps_aspect_impl,
    provides = [_DwyuDirectDepsCcInfo],
    attr_aspects = [],
)

def _mapping_to_direct_deps_impl(ctx):
    deps_cc = ctx.attr.target[_DwyuDirectDepsCcInfo]

    selected_compilation_contexts = [ctx.attr.target[CcInfo].compilation_context]
    for label, compilation_context in deps_cc.deps_to_compilation_context.items():
        if not ctx.attr.filter or str(label) in ctx.attr.filter:
            selected_compilation_contexts.append(compilation_context)

    aggregated_compilation_context = cc_common.merge_compilation_contexts(
        compilation_contexts = selected_compilation_contexts,
    )

    return DwyuRemappedCcInfo(
        target = ctx.attr.target.label,
        cc_info = CcInfo(
            compilation_context = aggregated_compilation_context,
            linking_context = ctx.attr.target[CcInfo].linking_context,
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
