load("@rules_cc//cc/common:cc_common.bzl", "cc_common")
load("@rules_cc//cc/common:cc_info.bzl", "CcInfo")
load(":common.bzl", "DwyuTransitiveDepsCcInfo", "cc_info_deps_from_all_attrs", "create_remapped_cc_info", "filter_compilation_contexts")
load(":providers.bzl", "DwyuRemappedCcInfo")

visibility("//dwyu/cc/cc_info_mapping/...")

def _aggregate_transitive_deps_greedily_aspect_impl(target, ctx):
    deps_to_compilation_context = {
        dependency.label: dependency[DwyuTransitiveDepsCcInfo].compilation_context
        for dependency in cc_info_deps_from_all_attrs(ctx.rule.attr)
        if DwyuTransitiveDepsCcInfo in dependency
    }

    aggregated_compilation_context = cc_common.merge_compilation_contexts(
        compilation_contexts = [target[CcInfo].compilation_context] + deps_to_compilation_context.values(),
    )

    return DwyuTransitiveDepsCcInfo(
        compilation_context = aggregated_compilation_context,
        deps_to_compilation_context = deps_to_compilation_context,
    )

_aggregate_transitive_deps_greedily_aspect = aspect(
    implementation = _aggregate_transitive_deps_greedily_aspect_impl,
    provides = [DwyuTransitiveDepsCcInfo],
    required_providers = [CcInfo],
    attr_aspects = ["*"],
)

def _mapping_to_transitive_deps_greedily_impl(ctx):
    return create_remapped_cc_info(
        target = ctx.attr.target,
        mapped_compilation_contexts = filter_compilation_contexts(
            deps_to_compilation_context = ctx.attr.target[DwyuTransitiveDepsCcInfo].deps_to_compilation_context,
            label_filter = ctx.attr.filter,
        ),
    )

mapping_to_transitive_deps_greedily = rule(
    implementation = _mapping_to_transitive_deps_greedily_impl,
    provides = [DwyuRemappedCcInfo],
    attrs = {
        "filter": attr.string_list(doc = "List of canonical target names of the direct dependencies which shall be mapped, together with all their transitive CcInfo dependencies."),
        "target": attr.label(aspects = [_aggregate_transitive_deps_greedily_aspect], providers = [CcInfo]),
    },
    doc = """
Make headers from all transitive CcInfo-providing dependencies available as if they were provided by the main target itself.
All rule attributes - with the exception of implementation_deps - are traversed recursively, and dependencies are followed only when they provide CcInfo.
We explicitly ignore implementation_deps, as allowing to map them would break their design of not being visible to users of the target.

By default, map all direct dependencies and their transitive CcInfo dependencies.
If the `filter` attribute is provided, only direct dependencies matching the canonical target names from the `filter` attribute are mapped together with their transitive CcInfo dependencies.
""",
)
