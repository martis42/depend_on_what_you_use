load("@rules_cc//cc/common:cc_info.bzl", "CcInfo")
load(":common.bzl", "DwyuDirectDepsCcInfo", "cc_info_deps_from_all_attrs", "create_remapped_cc_info", "filter_compilation_contexts")
load(":providers.bzl", "DwyuRemappedCcInfo")

visibility("//dwyu/cc/cc_info_mapping/...")

def _aggregate_direct_deps_greedily_aspect_impl(_, ctx):
    deps_to_compilation_context = {
        dependency.label: dependency[CcInfo].compilation_context
        for dependency in cc_info_deps_from_all_attrs(ctx.rule.attr)
        if CcInfo in dependency
    }

    return DwyuDirectDepsCcInfo(deps_to_compilation_context = deps_to_compilation_context)

_aggregate_direct_deps_greedily_aspect = aspect(
    implementation = _aggregate_direct_deps_greedily_aspect_impl,
    provides = [DwyuDirectDepsCcInfo],
    required_providers = [CcInfo],
    attr_aspects = [],
)

def _mapping_to_direct_deps_greedily_impl(ctx):
    return create_remapped_cc_info(
        target = ctx.attr.target,
        mapped_compilation_contexts = filter_compilation_contexts(
            deps_to_compilation_context = ctx.attr.target[DwyuDirectDepsCcInfo].deps_to_compilation_context,
            label_filter = ctx.attr.filter,
        ),
    )

mapping_to_direct_deps_greedily = rule(
    implementation = _mapping_to_direct_deps_greedily_impl,
    provides = [DwyuRemappedCcInfo],
    attrs = {
        "filter": attr.string_list(doc = "List of canonical target names of the direct dependencies which shall be mapped"),
        "target": attr.label(aspects = [_aggregate_direct_deps_greedily_aspect], providers = [CcInfo]),
    },
    doc = """
Make headers from direct CcInfo-providing dependencies available as if they were provided by the main target itself.
All rule attributes - with the exception of implementation_deps - are inspected.
We explicitly ignore implementation_deps, as allowing to map them would break their design of not being visible to users of the target.

By default map all direct dependencies.
If the `filter` attribute is provided, only map direct dependencies matching the canonical target names from the `filter` attribute.
""",
)
