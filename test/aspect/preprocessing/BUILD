load("@rules_cc//cc:cc_binary.bzl", "cc_binary")

cc_binary(
    name = "select_includes_via_macros",
    srcs = [
        "macros.h",
        "select_includes_via_macros.cpp",
    ],
    deps = [
        "//preprocessing/support:lib_a",
        "//preprocessing/support:lib_b",
        "//preprocessing/support:lib_c",
        "//preprocessing/support:lib_d",
        "//preprocessing/support:lib_e",
    ],
)

cc_binary(
    name = "select_includes_via_external_macros_with_defines",
    srcs = ["select_includes_via_external_macros.cpp"],
    defines = [
        "THE_ANSWER=42",
        "LIB_A_FILE_PATH='\"support/lib_a.h\"'",
    ],
    local_defines = ["TOGGLE"],
    deps = [
        "//preprocessing/support:lib_a",
        "//preprocessing/support:lib_b",
        "//preprocessing/support:lib_c",
    ],
)

cc_binary(
    name = "select_includes_via_external_macros_with_copts",
    srcs = ["select_includes_via_external_macros.cpp"],
    # Strictly speaking Windows does not automatically equal MSVC, but does so in our integration tests
    copts = select({
        "@platforms//os:windows": [
            "/DTOGGLE",
            "/DTHE_ANSWER=42",
            '/DLIB_A_FILE_PATH=\\"support/lib_a.h\\"',
        ],
        "//conditions:default": [
            "-DTOGGLE",
            "-DTHE_ANSWER=42",
            '-DLIB_A_FILE_PATH=\\"support/lib_a.h\\"',
        ],
    }),
    deps = [
        "//preprocessing/support:lib_a",
        "//preprocessing/support:lib_b",
        "//preprocessing/support:lib_c",
    ],
)

cc_binary(
    name = "select_includes_via_external_macros_with_cli_cxxopt",
    srcs = ["select_includes_via_external_macros.cpp"],
    # This target cannot build unless the required macros are defined via the CLI
    tags = ["manual"],
    deps = [
        "//preprocessing/support:lib_a",
        "//preprocessing/support:lib_b",
        "//preprocessing/support:lib_c",
    ],
)

cc_binary(
    name = "use_complex_libraries",
    srcs = ["use_complex_libraries.cpp"],
    deps = [
        "@boost.chrono",
        "@googletest//:gtest",
    ],
)
