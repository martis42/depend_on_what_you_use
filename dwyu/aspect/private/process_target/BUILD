load("@rules_cc//cc:cc_binary.bzl", "cc_binary")

cc_binary(
    name = "main_cc",
    srcs = ["main.cpp"],
    visibility = ["//visibility:public"],
    deps = [
        "//dwyu/private:program_options",
        "//dwyu/private:utils",
        "@nlohmann_json//:singleheader-json",
    ],
)
