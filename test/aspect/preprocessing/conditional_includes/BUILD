load("@rules_cc//cc:cc_binary.bzl", "cc_binary")

cc_binary(
    name = "select_includes_via_angle_brackets",
    srcs = ["select_includes_via_angle_brackets.cpp"],
    deps = [
        "//preprocessing/support:angle_lib_a",
        "//preprocessing/support:angle_lib_b",
        "//preprocessing/support:angle_lib_c",
    ],
)

cc_binary(
    name = "select_includes_via_cplusplus_define_overruling_std",
    srcs = ["select_includes_via_cplusplus_define_overruling_std.cpp"],
    copts = [
        "-std=c++23",
        # Manually set '__cplusplus' to C++11 inconsistent to C++23 defined via '-std=c++23'.
        # This shows the DWYU preprocessing behaves like the clang or gcc compiler if both '-std=...' and '__cplusplus=...' are provided.
        "-D__cplusplus=201103",
    ],
    deps = ["//preprocessing/support:lib_a"],
)

cc_binary(
    name = "select_includes_via_cpp_standard",
    srcs = ["select_includes_via_cpp_standard.cpp"],
    copts = [
        # Will use the wrong include if we don't enforce C++11
        "-std=c++11",
    ],
    deps = ["//preprocessing/support:lib_a"],
)

cc_binary(
    name = "select_includes_via_defines_and_undefs",
    srcs = ["select_includes_via_defines_and_undefs.cpp"],
    deps = [
        "//preprocessing/support:lib_a",
        "//preprocessing/support:lib_b",
        "//preprocessing/support:lib_c",
        "//preprocessing/support:lib_d",
    ],
)

cc_binary(
    name = "select_includes_via_dep_defines",
    srcs = ["select_includes_via_dep_defines.cpp"],
    deps = [
        "//preprocessing/conditional_includes/support:lib_exporting_defines",
        "//preprocessing/support:lib_a",
        "//preprocessing/support:lib_b",
        "//preprocessing/support:lib_c",
        "//preprocessing/support:lib_d",
    ],
)

cc_binary(
    name = "select_includes_via_dep_header_macros",
    srcs = ["select_includes_via_dep_header_macros.cpp"],
    local_defines = ["CONSUMER_DEFINE"],
    deps = [
        "//preprocessing/conditional_includes/support:lib_with_macros",
        "//preprocessing/support:lib_a",
        "//preprocessing/support:lib_b",
        "//preprocessing/support:lib_c",
        "//preprocessing/support:lib_d",
    ],
)

cc_binary(
    name = "select_includes_via_diagnostic_directives",
    srcs = ["select_includes_via_diagnostic_directives.cpp"],
    deps = [
        "//preprocessing/support:lib_a",
        "//preprocessing/support:lib_b",
        "//preprocessing/support:lib_c",
        "//preprocessing/support:lib_d",
    ],
)

cc_binary(
    name = "select_includes_via_directive_forms",
    srcs = ["select_includes_via_directive_forms.cpp"],
    deps = [
        "//preprocessing/support:lib_a",
        "//preprocessing/support:lib_b",
        "//preprocessing/support:lib_c",
        "//preprocessing/support:lib_d",
        "//preprocessing/support:lib_e",
        "//preprocessing/support:lib_f",
    ],
)

cc_binary(
    name = "select_includes_via_elif_and_nesting",
    srcs = ["select_includes_via_elif_and_nesting.cpp"],
    deps = [
        "//preprocessing/support:lib_a",
        "//preprocessing/support:lib_b",
        "//preprocessing/support:lib_c",
        "//preprocessing/support:lib_d",
        "//preprocessing/support:lib_e",
        "//preprocessing/support:lib_f",
    ],
)

cc_binary(
    name = "select_includes_via_elifdef",
    srcs = ["select_includes_via_elifdef.cpp"],
    copts = [
        # C++23 introduced '#elifdef' and '#elifndef'
        "-std=c++23",
    ],
    tags = [
        # boost.wave does not yet support '#elifdef' and '#elifndef'
        "manual",
    ],
    deps = [
        "//preprocessing/support:lib_a",
        "//preprocessing/support:lib_b",
        "//preprocessing/support:lib_c",
    ],
)

cc_binary(
    name = "select_includes_via_expressions",
    srcs = ["select_includes_via_expressions.cpp"],
    deps = [
        "//preprocessing/support:lib_a",
        "//preprocessing/support:lib_b",
        "//preprocessing/support:lib_c",
        "//preprocessing/support:lib_d",
        "//preprocessing/support:lib_e",
        "//preprocessing/support:lib_f",
        "//preprocessing/support:lib_g",
        "//preprocessing/support:lib_h",
    ],
)

cc_binary(
    name = "select_includes_via_external_macros_with_defines",
    srcs = ["select_includes_via_external_macros.cpp"],
    defines = [
        "THE_ANSWER=42",
        "LIB_A_FILE_PATH='\"preprocessing/support/lib_a.h\"'",
        "DEFAULT_VALUE_MACRO",
        "SQUARE_FROM_BUILD(x)=((x)*(x))",
    ],
    local_defines = ["TOGGLE"],
    deps = [
        "//preprocessing/support:lib_a",
        "//preprocessing/support:lib_b",
        "//preprocessing/support:lib_c",
        "//preprocessing/support:lib_d",
        "//preprocessing/support:lib_e",
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
            '/DLIB_A_FILE_PATH=\\"preprocessing/support/lib_a.h\\"',
            "/DDEFAULT_VALUE_MACRO",
            "/DSQUARE_FROM_BUILD(x)=((x)*(x))",
        ],
        "//conditions:default": [
            "-DTOGGLE",
            "-DTHE_ANSWER=42",
            '-DLIB_A_FILE_PATH=\\"preprocessing/support/lib_a.h\\"',
            "-DDEFAULT_VALUE_MACRO",
            "-DSQUARE_FROM_BUILD(x)=((x)*(x))",
        ],
    }),
    deps = [
        "//preprocessing/support:lib_a",
        "//preprocessing/support:lib_b",
        "//preprocessing/support:lib_c",
        "//preprocessing/support:lib_d",
        "//preprocessing/support:lib_e",
    ],
)

cc_binary(
    name = "select_includes_via_external_macros_with_cli_cxxopt",
    srcs = ["select_includes_via_external_macros.cpp"],
    tags = [
        # This target cannot build unless the required macros are defined via the CLI
        "manual",
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
    name = "select_includes_via_external_undefs",
    srcs = ["select_includes_via_external_undefs.cpp"],
    # Undefining is only possible via compiler flags, there is no equivalent for the 'defines' attributes
    copts = select({
        "@platforms//os:windows": [
            "/DCMDLINE_UNDEFINED",
            "/UCMDLINE_UNDEFINED",
            "/DCMDLINE_OVERRIDDEN=1",
        ],
        "//conditions:default": [
            "-DCMDLINE_UNDEFINED",
            "-UCMDLINE_UNDEFINED",
            "-DCMDLINE_OVERRIDDEN=1",
        ],
    }),
    deps = [
        "//preprocessing/support:lib_a",
        "//preprocessing/support:lib_b",
    ],
)

cc_binary(
    name = "select_includes_via_feature_test_macros",
    srcs = ["select_includes_via_feature_test_macros.cpp"],
    copts = [
        # C++20 standardized the feature test macros
        "-std=c++20",
    ],
    tags = [
        # boost.wave does not provide the compiler predefined feature test macros
        "manual",
    ],
    deps = [
        "//preprocessing/support:lib_a",
        "//preprocessing/support:lib_b",
        "//preprocessing/support:lib_c",
    ],
)

cc_binary(
    name = "select_includes_via_function_like_macros",
    srcs = ["select_includes_via_function_like_macros.cpp"],
    deps = [
        "//preprocessing/support:lib_a",
        "//preprocessing/support:lib_b",
        "//preprocessing/support:lib_c",
    ],
)

cc_binary(
    name = "select_includes_via_has_cpp_attribute",
    srcs = ["select_includes_via_has_cpp_attribute.cpp"],
    copts = [
        # C++20 standardized '__has_cpp_attribute'
        "-std=c++20",
    ],
    tags = [
        # boost.wave does not support '__has_cpp_attribute'
        "manual",
    ],
    deps = [
        "//preprocessing/support:lib_a",
        "//preprocessing/support:lib_b",
        "//preprocessing/support:lib_c",
        "//preprocessing/support:lib_d",
    ],
)

cc_binary(
    name = "select_includes_via_has_include",
    srcs = ["select_includes_via_has_include.cpp"],
    copts = [
        # C++17 introduced '__has_include'
        "-std=c++17",
    ],
    deps = [
        "//preprocessing/support:angle_lib_a",
        "//preprocessing/support:lib_a",
        "//preprocessing/support:lib_b",
        "//preprocessing/support:lib_c",
        "//preprocessing/support:lib_d",
        "//preprocessing/support:lib_e",
        "//preprocessing/support:lib_f",
        "//preprocessing/support:lib_g",
    ],
)

cc_binary(
    name = "select_includes_via_include_guards",
    srcs = ["select_includes_via_include_guards.cpp"],
    deps = [
        "//preprocessing/conditional_includes/support:lib_with_include_guards",
        "//preprocessing/support:lib_a",
        "//preprocessing/support:lib_b",
        "//preprocessing/support:lib_c",
        "//preprocessing/support:lib_d",
        "//preprocessing/support:lib_e",
        "//preprocessing/support:lib_f",
    ],
)

# Not a C++ standard feature, but a popular compiler extension supported by GCC and Clang
cc_binary(
    name = "select_includes_via_include_next",
    srcs = ["select_includes_via_include_next.cpp"],
    deps = [
        "//preprocessing/conditional_includes/support:lib_include_next_first",
        "//preprocessing/support:lib_a",
        "//preprocessing/support:lib_b",
        # TODO uncomment in when '__has_include_next' is fixed
        #"//preprocessing/support:lib_c",
    ],
)

cc_binary(
    name = "select_includes_via_lexical_forms",
    srcs = ["select_includes_via_lexical_forms.cpp"],
    deps = [
        "//preprocessing/support:lib_a",
        "//preprocessing/support:lib_b",
        "//preprocessing/support:lib_c",
    ],
)

cc_binary(
    name = "select_includes_via_predefined_macros",
    srcs = ["select_includes_via_predefined_macros.cpp"],
    deps = [
        "//preprocessing/conditional_includes/support:lib_with_include_level",
        "//preprocessing/support:lib_a",
        "//preprocessing/support:lib_b",
        "//preprocessing/support:lib_c",
    ],
)

cc_binary(
    name = "select_includes_via_raw_string_literal",
    srcs = ["select_includes_via_raw_string_literal.cpp"],
    tags = [
        # boost.wave does not ignore includes in raw string literals
        "manual",
    ],
    deps = ["//preprocessing/support:lib_a"],
)

cc_binary(
    name = "select_includes_via_token_pasting",
    srcs = ["select_includes_via_token_pasting.cpp"],
    deps = [
        "//preprocessing/support:lib_a",
        "//preprocessing/support:lib_b",
        "//preprocessing/support:lib_c",
        "//preprocessing/support:lib_d",
        "//preprocessing/support:lib_e",
    ],
)

cc_binary(
    name = "select_includes_via_variadic_macro",
    srcs = ["select_includes_via_variadic_macro.cpp"],
    copts = [
        # C++20 permits invoking a variadic macro without an argument for the variadic parameter
        "-std=c++20",
    ],
    deps = ["//preprocessing/support:lib_a"],
)

cc_binary(
    name = "use_complex_libraries",
    srcs = ["use_complex_libraries.cpp"],
    deps = [
        "//preprocessing/support:lib_a",
        "@googletest//:gtest",
    ],
)
