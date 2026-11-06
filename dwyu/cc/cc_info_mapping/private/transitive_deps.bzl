load("@rules_cc//cc/common:cc_common.bzl", "cc_common")
load("@rules_cc//cc/common:cc_info.bzl", "CcInfo")
load(":common.bzl", "DwyuTransitiveDepsCcInfo", "create_remapped_cc_info", "filter_compilation_contexts")
load(":providers.bzl", "DwyuRemappedCcInfo")

visibility("//dwyu/cc/cc_info_mapping/...")

def _aggregate_transitive_deps_aspect_impl(target, ctx):
    # A custom rule might offer CcInfo, but not have a 'deps' attribute.
    # We assume a custom rule using the concept of dependencies to other CcInfo provider targets would use the canonical 'deps' attribute.
    # Thus, we ignore targets without 'deps' attribute.
    deps_remapped_cc_info = {
        dep.label: dep[DwyuTransitiveDepsCcInfo].compilation_context
        for dep in getattr(ctx.rule.attr, "deps", [])
        if DwyuTransitiveDepsCcInfo in dep
    }

    aggregated_compilation_context = cc_common.merge_compilation_contexts(
        compilation_contexts = [target[CcInfo].compilation_context] + deps_remapped_cc_info.values(),
    )

    return DwyuTransitiveDepsCcInfo(
        compilation_context = aggregated_compilation_context,
        deps_to_compilation_context = deps_remapped_cc_info,
    )

_aggregate_transitive_deps_aspect = aspect(
    implementation = _aggregate_transitive_deps_aspect_impl,
    provides = [DwyuTransitiveDepsCcInfo],
    required_providers = [CcInfo],
    # We deliberately ignore implementation_deps since headers provided by them shall by design not be used by consumers of the target
    attr_aspects = ["deps"],
)

def _mapping_to_transitive_deps_impl(ctx):
    return create_remapped_cc_info(
        target = ctx.attr.target,
        mapped_compilation_contexts = filter_compilation_contexts(
            deps_to_compilation_context = ctx.attr.target[DwyuTransitiveDepsCcInfo].deps_to_compilation_context,
            label_filter = ctx.attr.filter,
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
