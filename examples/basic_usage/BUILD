load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "correct_dependencies",
    srcs = ["use_lib.cpp"],
    hdrs = ["use_lib.h"],
    # Usage of the library is an implementation detail
    implementation_deps = [":lib"],
    # The type is part of the public interface
    deps = [":my_type"],
)

cc_library(
    name = "false_dependencies",
    srcs = ["use_lib.cpp"],
    hdrs = ["use_lib.h"],
    # Missing 'deps' dependency to my_type
    deps = [
        ":lib",  # Used only in the cpp file and thus belongs to 'implementation_deps'
    ],
)

cc_library(
    name = "not_using_lib",
    hdrs = ["not_using_lib.h"],
    deps = [
        ":lib",  # Superfluous and unused dependency
        ":my_type",
    ],
)

cc_library(
    name = "my_type",
    hdrs = ["my_type.h"],
)

cc_library(
    name = "lib",
    hdrs = ["lib.h"],
    deps = [":my_type"],
)
