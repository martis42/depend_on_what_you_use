cc_library(
    name = "lib",
    hdrs = [
        "lib_part_a.h",
        "lib_part_b.h",
        "lib_part_c.h",
    ],
)

cc_binary(
    name = "utilization_low",
    srcs = ["utilization_low.cpp"],
    deps = [":lib"],
)

cc_binary(
    name = "utilization_high",
    srcs = ["utilization_high.cpp"],
    deps = [":lib"],
)
