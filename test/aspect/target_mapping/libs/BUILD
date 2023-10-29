cc_library(
    name = "a",
    hdrs = ["a.h"],
    visibility = ["//test/aspect/target_mapping:__subpackages__"],
    deps = [":b"],
)

cc_library(
    name = "b",
    hdrs = ["b.h"],
    visibility = ["//test/aspect/target_mapping/mapping:__pkg__"],
    deps = [":c"],
)

cc_library(
    name = "c",
    hdrs = ["c.h"],
)
