load("@rules_cc//cc/common:cc_common.bzl", "cc_common")
load("@rules_cc//cc/common:cc_info.bzl", "CcInfo")
load(":providers.bzl", "DwyuRemappedCcInfo")

visibility("//dwyu/cc/cc_info_mapping/...")

_DwyuExplicitTargetsCcInfo = provider(
    "Compilation contexts of targets we want to merge into the main target.",
    fields = {
        "targets_to_compilation_context": "Dictionary mapping the Label of a dependency to its CcInfo.compilation_context.",
    },
)

def _dict_diff(lhs, rhs):
    return {key: True for key in lhs if key not in rhs}

def _gather_compilation_context_from_deps_aspect_impl(target, ctx):
    targets_to_compilation_context = {target.label: target[CcInfo].compilation_context}
    for attr_name in dir(ctx.rule.attr):
        attr_value = getattr(ctx.rule.attr, attr_name)
        if type(attr_value) == "Target":
            dependencies = [attr_value]
        elif type(attr_value) == "list":
            dependencies = [dependency for dependency in attr_value if type(dependency) == "Target"]
        else:
            continue

        for dependency in dependencies:
            if _DwyuExplicitTargetsCcInfo in dependency:
                targets_to_compilation_context.update(dependency[_DwyuExplicitTargetsCcInfo].targets_to_compilation_context)

    return _DwyuExplicitTargetsCcInfo(targets_to_compilation_context = targets_to_compilation_context)

_gather_compilation_context_from_deps_aspect = aspect(
    implementation = _gather_compilation_context_from_deps_aspect_impl,
    provides = [_DwyuExplicitTargetsCcInfo],
    required_providers = [CcInfo],
    # Traverse every label-bearing attribute to support custom C++ rules.
    attr_aspects = ["*"],
)

def _mapping_to_transitive_deps_impl(ctx):
    targets_cc = ctx.attr.target[_DwyuExplicitTargetsCcInfo]

    matched_targets = {}
    selected_compilation_contexts = [ctx.attr.target[CcInfo].compilation_context]
    if ctx.attr.mapped_targets:
        for label, compilation_context in targets_cc.targets_to_compilation_context.items():
            if str(label) in ctx.attr.mapped_targets:
                selected_compilation_contexts.append(compilation_context)
                matched_targets[str(label)] = True

    if len(matched_targets) != len(ctx.attr.mapped_targets):
        fail("Some 'mapped_targets' were not found in the dependency tree: {}".format(_dict_diff(ctx.attr.mapped_targets, matched_targets).keys()))

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

mapping_to_explicit_deps = rule(
    implementation = _mapping_to_transitive_deps_impl,
    provides = [DwyuRemappedCcInfo],
    attrs = {
        "mapped_targets": attr.string_list(doc = "List of canonical target names for which their compilation context shall be mapped to 'target'."),
        "target": attr.label(aspects = [_gather_compilation_context_from_deps_aspect], providers = [CcInfo]),
    },
    doc = """
Make headers from all mapped targets available as if they where provided by the main target itself.
We do so by merging the compilation_context information from the targets into the main target's CcInfo.
Only targets from the dependency tree of the main targets are valid input for mapping.
""",
)
