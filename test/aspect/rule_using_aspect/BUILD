load("//rule_using_aspect:rule.bzl", "dwyu_rule_direct", "dwyu_rule_recursive", "dwyu_rule_recursive_with_impl_deps")

dwyu_rule_direct(
    name = "dwyu_direct_main",
    deps = [":main"],
)

dwyu_rule_recursive(
    name = "dwyu_recursive_main",
    tags = [
        "manual",  # This target is supposed to fail, thus only build it if explicitly requested
    ],
    deps = [":main"],
)

dwyu_rule_recursive_with_impl_deps(
    name = "dwyu_recursive_with_impl_deps",
    tags = [
        "manual",  # This target is supposed to fail, thus only build it if explicitly requested
    ],
    deps = [":use_impl_deps"],
)

##
## Support Targets
##

cc_binary(
    name = "main",
    srcs = ["main.cpp"],
    deps = [":a"],
)

cc_library(
    name = "a",
    hdrs = ["a.h"],
    deps = [":b"],
)

cc_library(
    name = "b",
    hdrs = ["b.h"],
    deps = [
        ":c",  # unused dependency
    ],
)

cc_library(
    name = "c",
    hdrs = ["c.h"],
)

cc_library(
    name = "use_impl_deps",
    srcs = ["use_impl_deps.cpp"],
    implementation_deps = [":a"],
)
