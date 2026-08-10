load("@rules_cc//cc/common:cc_common.bzl", "cc_common")
load("@rules_cc//cc/common:cc_info.bzl", "CcInfo")
load(":providers.bzl", "DwyuRemappedCcInfo")

visibility("//dwyu/cc/cc_info_mapping/...")

_DwyuDirectDepsCcInfo = provider(
    "Compilation contexts of a target and its direct dependencies, to be filtered and merged by the rule using this aspect.",
    fields = {
        "compilation_contexts": "dict mapping the Label of a direct dependency providing CcInfo to its compilation_context",
    },
)

def _aggregate_direct_deps_aspect_impl(target, ctx):
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

    return _DwyuDirectDepsCcInfo(compilation_contexts = dep_compilation_contexts)

_aggregate_direct_deps_aspect = aspect(
    implementation = _aggregate_direct_deps_aspect_impl,
    provides = [_DwyuDirectDepsCcInfo],
    attr_aspects = [],
)

def _mapping_to_direct_deps_impl(ctx):
    cc_info = ctx.attr.target[CcInfo]
    deps_cc_info = ctx.attr.target[_DwyuDirectDepsCcInfo]

    # TODO better string based logic
    # Canonical labels are absolute, so resolving them via Label() here is not affected by this .bzl file's package.
    filter_labels = [Label(canonical_name) for canonical_name in ctx.attr.filter]

    selected_compilation_contexts = [cc_info.compilation_context]
    for label, compilation_context in deps_cc_info.compilation_contexts.items():
        if not filter_labels or label in filter_labels:
            selected_compilation_contexts.append(compilation_context)

    aggregated_compilation_context = cc_common.merge_compilation_contexts(
        compilation_contexts = selected_compilation_contexts,
    )

    return DwyuRemappedCcInfo(
        target = ctx.attr.target.label,
        cc_info = CcInfo(
            compilation_context = aggregated_compilation_context,
            linking_context = cc_info.linking_context,
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
