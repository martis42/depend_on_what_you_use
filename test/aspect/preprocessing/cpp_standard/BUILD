load("@rules_cc//cc:cc_binary.bzl", "cc_binary")

cc_binary(
    name = "custom_cplusplus_overrules_std",
    srcs = ["custom_cplusplus_overrules_std.cpp"],
    copts = [
        "-std=c++23",
        # Manually set '__cplusplus' to C++11 inconsistent to C++23 defined via '-std=c++23'.
        # This shows the DWYU preprocessing behaves like the clang or gcc compiler if both '-std=...' and '__cplusplus=...' are provided.
        "-D__cplusplus=201103",
    ],
    deps = ["//preprocessing/support:lib_a"],
)

cc_binary(
    name = "set_cpp_standard",
    srcs = ["set_cpp_standard.cpp"],
    copts = [
        # Will use the wrong include if we don't enforce C++11
        "-std=c++11",
    ],
    deps = ["//preprocessing/support:lib_a"],
)

cc_binary(
    name = "support_has_include",
    srcs = ["support_has_include.cpp"],
    copts = [
        # C++17 introduced '__has_include'
        "-std=c++17",
    ],
    deps = [
        "//preprocessing/support:lib_a",
        "//preprocessing/support:lib_b",
    ],
)

cc_binary(
    name = "support_variadic_macro",
    srcs = ["support_variadic_macro.cpp"],
    copts = [
        # C++20 introduced variadic macros
        "-std=c++20",
    ],
    deps = ["//preprocessing/support:lib_a"],
)
