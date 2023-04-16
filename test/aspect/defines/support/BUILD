cc_library(
    name = "transitive_define",
    copts = ["-DLOCAL_COPT"],  # should not influence other targets
    defines = ["TRANSITIVE_DEFINE"],
    local_defines = ["LOCAL_DEFINE"],  # should not influence other targets
    visibility = ["//test/aspect/defines:__pkg__"],
)
