filegroup(
    name = "custom_config",
    srcs = ["custom_config.json"],
    visibility = ["//visibility:public"],
)

# Has an invalid include, which does however not cause an error due to the ognore list in the config
cc_library(
    name = "foo",
    hdrs = ["foo.h"],
)
