load("@rules_cc//cc/common:cc_common.bzl", "cc_common")
load("@rules_cc//cc/common:cc_info.bzl", "CcInfo")
load(":providers.bzl", "DwyuRemappedCcInfo")

visibility("//dwyu/cc/cc_info_mapping/...")

_DwyuTransitiveDepsCcInfo = provider(
    "Cc_info of a target's direct dependencies, each already recursively aggregated, to be filtered and merged by the rule using this aspect.",
    fields = {
        "dep_cc_infos": "dict mapping the Label of a direct dependency to its recursively aggregated CcInfo",
    },
)

def _aggregate_transitive_deps_aspect_impl(target, ctx):
    # A custom rule might offer CcInfo, but not have a 'deps' attribute.
    # We assume a custom rule using the concept of dependencies to other CcInfo provider targets would use the canonical 'deps' attribute and ignore targets without 'deps' attribute.
    deps_remapped_cc_infos = {
        dep.label: dep[DwyuRemappedCcInfo].cc_info
        for dep in getattr(ctx.rule.attr, "deps", [])
    }

    # 'cc_*' targets can depend on things like sh_library not providing CcInfo at all
    if CcInfo not in target:
        return [
            DwyuRemappedCcInfo(target = target.label, cc_info = CcInfo()),
            _DwyuTransitiveDepsCcInfo(dep_cc_infos = deps_remapped_cc_infos),
        ]

    aggregated_compilation_context = cc_common.merge_compilation_contexts(
        compilation_contexts = [target[CcInfo].compilation_context] + [cci.compilation_context for cci in deps_remapped_cc_infos.values()],
    )

    return [
        DwyuRemappedCcInfo(
            target = target.label,
            cc_info = CcInfo(compilation_context = aggregated_compilation_context),
        ),
        _DwyuTransitiveDepsCcInfo(dep_cc_infos = deps_remapped_cc_infos),
    ]

_aggregate_transitive_deps_aspect = aspect(
    implementation = _aggregate_transitive_deps_aspect_impl,
    provides = [DwyuRemappedCcInfo, _DwyuTransitiveDepsCcInfo],
    # We deliberately ignore implementation_deps since headers provided by them shall by design not be used by consumers of the target
    attr_aspects = ["deps"],
)

def _mapping_to_transitive_deps_impl(ctx):
    cc_info = ctx.attr.target[CcInfo]
    deps_cc_info = ctx.attr.target[_DwyuTransitiveDepsCcInfo]

    # TODO better string based logic
    # Canonical labels are absolute, so resolving them via Label() here is not affected by this .bzl file's package.
    filter_labels = [Label(canonical_name) for canonical_name in ctx.attr.filter]

    selected_compilation_contexts = [cc_info.compilation_context]
    for label, cc_info in deps_cc_info.dep_cc_infos.items():
        if not filter_labels or label in filter_labels:
            selected_compilation_contexts.append(cc_info.compilation_context)

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

mapping_to_transitive_deps = rule(
    implementation = _mapping_to_transitive_deps_impl,
    provides = [DwyuRemappedCcInfo],
    attrs = {
        "filter": attr.string_list(doc = "List of canonical target names of the direct dependencies which shall be mapped, together with their own transitive dependencies"),
        "target": attr.label(aspects = [_aggregate_transitive_deps_aspect], providers = [CcInfo]),
    },
    doc = """
Make headers from all transitive dependencies available as if they where provided by the main target itself.
We do so by recursively merging the compilation_context information from the dependencies into the main target's CcInfo.
We explicitly ignore implementation_deps, as allowing to map them would break their design of not being visible to users of the target.

By default map all direct dependencies and, recursively, their own transitive dependencies.
If the `filter` attribute is provided, only direct dependencies matching the canonical target names from the `filter` attribute (together with their own transitive dependencies) are mapped.
""",
)
