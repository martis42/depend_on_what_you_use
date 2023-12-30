load(":rule.bzl", "dwyu_rule")

cc_library(
    name = "bad_target",
    hdrs = ["bad_target.h"],
)

dwyu_rule(
    name = "dwyu",
    deps = [":bad_target"],
)
