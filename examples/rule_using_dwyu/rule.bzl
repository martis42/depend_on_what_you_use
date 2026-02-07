load("//:aspect.bzl", "dwyu")

def _dwyu_rule_impl(ctx):
    # gather artifacts to make sure the DWYU aspect is executed
    dwyu_artifacts = depset(transitive = [dep[OutputGroupInfo].dwyu for dep in ctx.attr.deps])
    return [DefaultInfo(files = dwyu_artifacts)]

dwyu_rule = rule(
    implementation = _dwyu_rule_impl,
    attrs = {
        # You can control what this rule does (e.g. recursive vs. non recursive analysis) by specifying a DWYU aspect
        # which is configured in the desired way here.
        "deps": attr.label_list(aspects = [dwyu]),
        # Some DWYU flags can be controlled via '--aspects_parameters'. If their default value is 'False', they have to
        # be set explicitly by the rule wrapper.
        "dwyu_analysis_optimizes_impl_deps": attr.bool(default = True),
        "dwyu_verbose": attr.bool(default = False),
    },
)
