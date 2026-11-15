load("@rules_cc//cc/common:cc_info.bzl", "CcInfo")
load("//dwyu/cc/cc_info_mapping:providers.bzl", "DwyuRemappedCcInfo")
load(":common.bzl", "cc_info_deps_from_all_attrs", "create_remapped_cc_info")

visibility("//dwyu/cc/cc_info_mapping/...")

_DwyuExplicitTargetsCcInfo = provider(
    "Compilation contexts of targets we want to merge into the main target.",
    fields = {
        "targets_to_compilation_context": "Dictionary mapping the Label of a dependency to its CcInfo.compilation_context.",
    },
)

def _gather_compilation_context_from_deps_aspect_impl(target, ctx):
    targets_to_compilation_context = {target.label: target[CcInfo].compilation_context}
    for dependency in cc_info_deps_from_all_attrs(ctx.rule.attr, skip_impl_deps = False):
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

    mapped_targets = set(ctx.attr.mapped_targets)
    matched_targets = set()
    selected_compilation_contexts = []
    if mapped_targets:
        for label, compilation_context in targets_cc.targets_to_compilation_context.items():
            if str(label) in mapped_targets:
                selected_compilation_contexts.append(compilation_context)
                matched_targets.add(str(label))

    if len(matched_targets) != len(ctx.attr.mapped_targets):
        fail("Some 'mapped_targets' were not found in the dependency tree: {}".format(list(mapped_targets - matched_targets)))

    return create_remapped_cc_info(
        target = ctx.attr.target,
        mapped_compilation_contexts = selected_compilation_contexts,
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
