load("@rules_cc//cc:cc_binary.bzl", "cc_binary")

cc_binary(
    name = "main",
    srcs = ["main.cpp"],
    visibility = ["//visibility:public"],
    deps = [
        "//dwyu/aspect/private/preprocessing/fast_parsing:process_files",
        "//dwyu/aspect/private/preprocessing/wave:preprocessing_hooks",
        "//dwyu/aspect/private/preprocessing/wave:process_files",
        "//dwyu/private:program_options",
        "//dwyu/private:utils",
        "@boost.wave//:wave",
        "@nlohmann_json//:singleheader-json",
    ],
)
