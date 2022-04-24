cc_library(
    name = "prefixed",
    srcs = ["prefixed.cpp"],
    hdrs = ["prefixed.h"],
    include_prefix = "virtual/prefix",
)

cc_library(
    name = "stripped",
    srcs = ["stripped.cpp"],
    hdrs = ["some/sub/dir/stripped.h"],
    strip_include_prefix = "some",
)

cc_binary(
    name = "use_prefixed",
    srcs = ["use_prefixed.cpp"],
    deps = [":prefixed"],
)

cc_binary(
    name = "use_stripped",
    srcs = ["use_stripped.cpp"],
    deps = [":stripped"],
)
