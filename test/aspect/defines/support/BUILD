package(default_visibility = ["//defines:__pkg__"])

cc_library(
    name = "transitive_define",
    copts = ["-DLOCAL_COPT"],  # should not influence other targets
    defines = ["TRANSITIVE_DEFINE"],
    local_defines = ["LOCAL_DEFINE"],  # should not influence other targets
)

cc_library(
    name = "conditional_defines",
    hdrs = ["conditional_defines.h"],
    deps = [":some_defines"],
)

cc_library(
    name = "some_defines",
    hdrs = ["some_defines.h"],
)

cc_library(
    name = "lib_a",
    hdrs = ["a.h"],
)

cc_library(
    name = "lib_b",
    hdrs = ["b.h"],
)

cc_library(
    name = "lib_c",
    hdrs = ["c.h"],
)
