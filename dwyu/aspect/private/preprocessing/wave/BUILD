load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "preprocessing_hooks",
    hdrs = [
        "gather_direct_includes_hook.h",
        "preprocessing_hook_base.h",
    ],
    visibility = ["//dwyu/aspect/private/preprocessing:__subpackages__"],
    deps = [
        "//dwyu/aspect/private/preprocessing/lib:included_file",
        "@boost.wave//:wave",
        "@boost//:filesystem",
    ],
)
