load("//test/aspect/recursion:rule.bzl", "dwyu_rule_direct", "dwyu_rule_recursive", "dwyu_rule_recursive_with_impl_deps")

# Has a diamond dependency towards C through A and B
# main specifies its dependencies correctly, but C has an error
cc_binary(
    name = "main",
    srcs = ["main.cpp"],
    deps = [
        ":a",
        ":b",
    ],
)

dwyu_rule_direct(
    name = "dwyu_direct_main",
    deps = [":main"],
)

dwyu_rule_recursive(
    name = "dwyu_recursive_main",
    deps = [":main"],
)

cc_library(
    name = "a",
    hdrs = ["a.h"],
    deps = [":c"],
)

cc_library(
    name = "b",
    hdrs = ["b.h"],
    deps = [":c"],
)

cc_library(
    name = "c",
    hdrs = ["c.h"],
    deps = [
        ":d",
        ":e",  # unused dependency
    ],
)

cc_library(
    name = "d",
    hdrs = ["d.h"],
)

cc_library(
    name = "e",
    hdrs = ["e.h"],
)

cc_library(
    name = "use_impl_deps",
    srcs = ["use_impl_deps.cpp"],
    implementation_deps = [":a"],
)

dwyu_rule_recursive_with_impl_deps(
    name = "dwyu_recursive_use_impl_deps",
    deps = [":use_impl_deps"],
)
