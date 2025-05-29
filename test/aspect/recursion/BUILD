load("@rules_cc//cc:cc_binary.bzl", "cc_binary")
load("@rules_cc//cc:cc_library.bzl", "cc_library")

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

cc_library(
    name = "use_impl_deps",
    srcs = ["use_impl_deps.cpp"],
    implementation_deps = [":a"],
)

##
## Support Targets
##

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

# Skipping DWYU on this target demonstrates that the recursive analysis and DWYU report aggregation work, even if DWYU
# is not executed on some targets
cc_library(
    name = "e",
    hdrs = ["e.h"],
    tags = ["no-dwyu"],
    deps = [":f"],  # unused dependency
)

cc_library(
    name = "f",
    hdrs = ["f.h"],
)
