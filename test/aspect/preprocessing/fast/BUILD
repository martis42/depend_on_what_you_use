load("@rules_cc//cc:cc_binary.bzl", "cc_binary")

cc_binary(
    name = "no_preprocessing",
    srcs = ["no_preprocessing.cpp"],
    deps = [
        # Unless preprocessing is disabled one of both deps will always be unused
        "//preprocessing/support:lib_a",
        "//preprocessing/support:lib_b",
    ],
)

cc_binary(
    name = "no_preprocessing_with_preprocessing_chosen_by_tag",
    srcs = ["no_preprocessing.cpp"],
    tags = ["dwyu:preprocessing_mode=fast"],
    deps = [
        # Unless preprocessing is disabled one of both deps will always be unused
        "//preprocessing/support:lib_a",
        "//preprocessing/support:lib_b",
    ],
)
