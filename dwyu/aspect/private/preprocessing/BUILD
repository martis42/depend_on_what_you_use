load("@rules_cc//cc:cc_binary.bzl", "cc_binary")

cc_binary(
    name = "main",
    srcs = ["main.cpp"],
    visibility = ["//visibility:public"],
    deps = [
        "//dwyu/aspect/private/preprocessing/lib:included_file",
        "//dwyu/aspect/private/preprocessing/wave:preprocessing_hooks",
        "//dwyu/private:program_options",
        "//dwyu/private:utils",
        "@boost.wave//:wave",
        "@nlohmann_json//:singleheader-json",
    ],
)

cc_binary(
    name = "main_no_preprocessing",
    srcs = ["main_no_preprocessing.cpp"],
    visibility = ["//visibility:public"],
    deps = [
        "//dwyu/aspect/private/preprocessing/fast_parsing:extract_includes",
        "//dwyu/aspect/private/preprocessing/lib:included_file",
        "//dwyu/private:program_options",
        "//dwyu/private:utils",
        "@boost.wave//:wave",
        "@boost//:filesystem",
        "@nlohmann_json//:singleheader-json",
    ],
)
