cc_library(
    name = "used",
    hdrs = ["used.h"],
)

cc_library(
    name = "unused",
    hdrs = ["unused.h"],
)

cc_binary(
    name = "main",
    srcs = ["main.cpp"],
    deps = [
        ":unused",
        ":used",
    ],
)
