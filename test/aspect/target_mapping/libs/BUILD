cc_library(
    name = "a",
    hdrs = ["a.h"],
    visibility = ["//target_mapping:__subpackages__"],
    deps = [
        ":b",
        # Test travsing direct deps is robust against non C/CPP deps
        ":non_cc_thing",
    ],
)

cc_library(
    name = "b",
    hdrs = ["b.h"],
    visibility = ["//target_mapping/mapping:__pkg__"],
    deps = [
        ":c",
        # Test travsing transitive deps is robust against non C/CPP deps
        ":non_cc_thing",
    ],
)

cc_library(
    name = "c",
    hdrs = ["c.h"],
)

sh_library(
    name = "non_cc_thing",
    srcs = ["non_cc_thing.sh"],
)
