load("@rules_cc//cc/common:cc_common.bzl", "cc_common")
load("@rules_cc//cc/common:cc_info.bzl", "CcInfo")
load(":providers.bzl", "DwyuRemappedCcInfo")

visibility("//dwyu/cc/cc_info_mapping/...")

_DwyuGreedyDirectDepsCcInfo = provider(
    "Compilation contexts of CcInfo-providing targets found in all rule attributes.",
    fields = {
        "deps_to_compilation_context": "Dictionary mapping a direct dependency Label to its CcInfo.compilation_context",
    },
)

def _cc_info_dependencies(rule_attrs):
    dependencies = []
    for attr_name in dir(rule_attrs):
        if attr_name == "implementation_deps":
            # We deliberately ignore implementation_deps since headers provided by them shall by design not be used by consumers of the target.
            continue
        attr_value = getattr(rule_attrs, attr_name)
        if type(attr_value) == "Target":
            dependencies.append(attr_value)
        elif type(attr_value) == "list":
            dependencies.extend([dependency for dependency in attr_value if type(dependency) == "Target"])
    return dependencies

def _aggregate_direct_deps_greedily_aspect_impl(_, ctx):
    deps_to_compilation_context = {
        dependency.label: dependency[CcInfo].compilation_context
        for dependency in _cc_info_dependencies(ctx.rule.attr)
        if CcInfo in dependency
    }

    return _DwyuGreedyDirectDepsCcInfo(deps_to_compilation_context = deps_to_compilation_context)

_aggregate_direct_deps_greedily_aspect = aspect(
    implementation = _aggregate_direct_deps_greedily_aspect_impl,
    provides = [_DwyuGreedyDirectDepsCcInfo],
    required_providers = [CcInfo],
    attr_aspects = [],
)

def _mapping_to_direct_deps_greedily_impl(ctx):
    deps_cc = ctx.attr.target[_DwyuGreedyDirectDepsCcInfo]

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
