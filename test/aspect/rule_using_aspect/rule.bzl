load("//:aspect.bzl", "dwyu", "dwyu_cpp")
load("//rule_using_aspect:aspect.bzl", "dwyu_recursive", "dwyu_recursive_cpp", "dwyu_recursive_impl_deps", "dwyu_recursive_impl_deps_cpp")

def _dwyu_rule_impl(ctx):
    # gather artifacts to make sure the aspect is executed
    aspect_artifacts = depset(transitive = [dep[OutputGroupInfo].dwyu for dep in ctx.attr.deps])
    return [DefaultInfo(files = aspect_artifacts)]

dwyu_rule_direct = rule(
    implementation = _dwyu_rule_impl,
    attrs = {
        "deps": attr.label_list(aspects = [dwyu]),
    },
)

dwyu_rule_recursive = rule(
    implementation = _dwyu_rule_impl,
    attrs = {
        "deps": attr.label_list(aspects = [dwyu_recursive]),
    },
)

dwyu_rule_recursive_with_impl_deps = rule(
    implementation = _dwyu_rule_impl,
    attrs = {
        "deps": attr.label_list(aspects = [dwyu_recursive_impl_deps]),
    },
)

dwyu_rule_direct_cpp = rule(
    implementation = _dwyu_rule_impl,
    attrs = {
        "deps": attr.label_list(aspects = [dwyu_cpp]),
    },
)

dwyu_rule_recursive_cpp = rule(
    implementation = _dwyu_rule_impl,
    attrs = {
        "deps": attr.label_list(aspects = [dwyu_recursive_cpp]),
    },
)

dwyu_rule_recursive_with_impl_deps_cpp = rule(
    implementation = _dwyu_rule_impl,
    attrs = {
        "deps": attr.label_list(aspects = [dwyu_recursive_impl_deps_cpp]),
    },
)
