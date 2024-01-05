load(":rule.bzl", "dwyu_rule")

cc_library(
    name = "bad_target",
    hdrs = ["bad_target.h"],
)

dwyu_rule(
    name = "dwyu",
    tags = [
        "manual",  # This target is supposed to fail, thus only build it if explicitly requested
    ],
    deps = [":bad_target"],
)
