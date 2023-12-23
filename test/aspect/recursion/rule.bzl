load("//test/aspect:aspect.bzl", "dwyu_default_aspect")
load("//test/aspect/recursion:aspect.bzl", "recursive_aspect", "recursive_impl_deps_aspect")

def _dwyu_rule_impl(ctx):
    # gather artifacts to make sure the aspect is executed
    aspect_artifacts = depset(transitive = [dep[OutputGroupInfo].dwyu for dep in ctx.attr.deps])
    return [DefaultInfo(files = aspect_artifacts)]

dwyu_rule_direct = rule(
    implementation = _dwyu_rule_impl,
    attrs = {
        "deps": attr.label_list(aspects = [dwyu_default_aspect]),
    },
)

dwyu_rule_recursive = rule(
    implementation = _dwyu_rule_impl,
    attrs = {
        "deps": attr.label_list(aspects = [recursive_aspect]),
    },
)

dwyu_rule_recursive_with_impl_deps = rule(
    implementation = _dwyu_rule_impl,
    attrs = {
        "deps": attr.label_list(aspects = [recursive_impl_deps_aspect]),
    },
)
