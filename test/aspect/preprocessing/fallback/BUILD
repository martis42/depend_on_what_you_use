load("@rules_cc//cc:cc_binary.bzl", "cc_binary")
load("@rules_cc//cc:cc_library.bzl", "cc_library")

# The targets here use preprocessor constructs which boost::wave cannot evaluate in our C++11 language mode.
# The preprocessing recovers from this by falling back to lexically scanning the affected file for include statements.
# Without the fallback, include statements after such constructs are silently dropped and the dependencies providing
# them are falsely reported as unused.

cc_binary(
    name = "use_empty_variadic_macro",
    srcs = ["use_empty_variadic_macro.cpp"],
    deps = [
        ":lib_used_after_problematic_construct",
        ":variadic_macro",
    ],
)

cc_binary(
    name = "use_has_include_guard",
    srcs = ["use_has_include_guard.cpp"],
    deps = [
        ":lib_guarded_by_has_include",
        ":lib_used_after_problematic_construct",
    ],
)

cc_binary(
    name = "use_unbalanced_conditional_header",
    srcs = ["use_unbalanced_conditional_header.cpp"],
    deps = [
        ":lib_ending_inside_conditional",
        ":lib_used_after_problematic_construct",
    ],
)

cc_binary(
    name = "use_with_unused_dep",
    srcs = ["use_empty_variadic_macro.cpp"],
    deps = [
        ":lib_unused",
        ":lib_used_after_problematic_construct",
        ":variadic_macro",
    ],
)

cc_library(
    name = "variadic_macro",
    hdrs = ["variadic_macro.h"],
)

cc_library(
    name = "lib_guarded_by_has_include",
    hdrs = ["lib_guarded_by_has_include.h"],
)

cc_library(
    name = "lib_ending_inside_conditional",
    hdrs = ["lib_ending_inside_conditional.h"],
)

cc_library(
    name = "lib_used_after_problematic_construct",
    hdrs = ["lib_used_after_problematic_construct.h"],
)

cc_library(
    name = "lib_unused",
    hdrs = ["lib_unused.h"],
)
