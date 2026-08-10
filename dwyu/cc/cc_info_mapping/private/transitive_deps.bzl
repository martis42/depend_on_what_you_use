load("@rules_cc//cc/common:cc_common.bzl", "cc_common")
load("@rules_cc//cc/common:cc_info.bzl", "CcInfo")
load(":providers.bzl", "DwyuRemappedCcInfo")

visibility("//dwyu/cc/cc_info_mapping/...")

_DwyuTransitiveDepsCcInfo = provider(
    "Compilation contexts of dependencies, to be filtered and merged by the rule using this aspect.",
    fields = {
        "compilation_context": "compilation_context provided by this target, which has all compilation_context from the transitive dependencies merged in.",
        "deps_to_compilation_context": "Dictionary mapping the Label of a dependency to its CcInfo.compilation_context. All transitive dependencies of this dependency are merged into this compilation_context.",
    },
)

def _aggregate_transitive_deps_aspect_impl(target, ctx):
    # A custom rule might offer CcInfo, but not have a 'deps' attribute.
    # We assume a custom rule using the concept of dependencies to other CcInfo provider targets would use the canonical 'deps' attribute.
    # Thus, we ignore targets without 'deps' attribute.
    deps_remapped_cc_info = {
        dep.label: dep[_DwyuTransitiveDepsCcInfo].compilation_context
        for dep in getattr(ctx.rule.attr, "deps", [])
    }

    # 'cc_*' targets can depend on things like sh_library not providing CcInfo at all
    if CcInfo not in target:
        return _DwyuTransitiveDepsCcInfo(
            compilation_context = cc_common.create_compilation_context(),
            deps_to_compilation_context = deps_remapped_cc_info,
        )

    aggregated_compilation_context = cc_common.merge_compilation_contexts(
        compilation_contexts = [target[CcInfo].compilation_context] + deps_remapped_cc_info.values(),
    )

    return _DwyuTransitiveDepsCcInfo(
        compilation_context = aggregated_compilation_context,
        deps_to_compilation_context = deps_remapped_cc_info,
    )

_aggregate_transitive_deps_aspect = aspect(
    implementation = _aggregate_transitive_deps_aspect_impl,
    provides = [_DwyuTransitiveDepsCcInfo],
    # We deliberately ignore implementation_deps since headers provided by them shall by design not be used by consumers of the target
    attr_aspects = ["deps"],
)

def _mapping_to_transitive_deps_impl(ctx):
    deps_cc = ctx.attr.target[_DwyuTransitiveDepsCcInfo]

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

By default map all direct dependencies and their own transitive dependencies.
If the `filter` attribute is provided, only direct dependencies matching the canonical target names from the `filter` attribute are mapped together with their own transitive dependencies.
One cannot filter transitive dependencies with the `filter` attribute.
""",
)
