load("@depend_on_what_you_use//dwyu/cc/cc_info_mapping:providers.bzl", "DwyuRemappedCcInfo")
load("@rules_cc//cc/common:cc_common.bzl", "cc_common")
load("@rules_cc//cc/common:cc_info.bzl", "CcInfo")

_DirectDepsInfo = provider(
    "Compilation contexts of direct dependencies, keyed by label.",
    fields = ["contexts"],
)

def _direct_deps_impl(_target, ctx):
    return [_DirectDepsInfo(contexts = {
        dep.label: dep[CcInfo].compilation_context
        for dep in getattr(ctx.rule.attr, "deps", [])
        if CcInfo in dep
    })]

_direct_deps = aspect(
    implementation = _direct_deps_impl,
    attr_aspects = [],
    required_providers = [CcInfo],
)

def _custom_remapping_impl(ctx):
    original = ctx.attr.target[CcInfo]
    contexts = [original.compilation_context] + [
        context
        for label, context in ctx.attr.target[_DirectDepsInfo].contexts.items()
        if label.name.startswith(ctx.attr.name_prefix)
    ]
    return [DwyuRemappedCcInfo(
        target = ctx.attr.target.label,
        cc_info = CcInfo(
            compilation_context = cc_common.merge_compilation_contexts(compilation_contexts = contexts),
            linking_context = original.linking_context,
        ),
    )]

custom_remapping = rule(
    doc = "Custom remapping rule for DWYU target mapping mapping all direct dependencies starting with a certain prefix.",
    implementation = _custom_remapping_impl,
    attrs = {
        "name_prefix": attr.string(mandatory = True),
        "target": attr.label(mandatory = True, providers = [CcInfo], aspects = [_direct_deps]),
    },
    provides = [DwyuRemappedCcInfo],
)
