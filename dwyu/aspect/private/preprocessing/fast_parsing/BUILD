load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "extract_includes",
    srcs = ["extract_includes.cpp"],
    hdrs = ["extract_includes.h"],
    visibility = ["//dwyu/aspect/private/preprocessing:__subpackages__"],
)

cc_library(
    name = "process_files",
    srcs = ["process_files.cpp"],
    hdrs = ["process_files.h"],
    implementation_deps = [
        ":extract_includes",
        "//dwyu/aspect/private/preprocessing/lib:included_file",
        "//dwyu/private:utils",
        "@boost.wave//:wave",
        "@boost//:filesystem",
    ],
    visibility = ["//dwyu/aspect/private/preprocessing:__subpackages__"],
    deps = [
        "@nlohmann_json//:singleheader-json",
    ],
)
