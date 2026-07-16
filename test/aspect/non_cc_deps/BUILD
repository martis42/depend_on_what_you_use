load("@rules_cc//cc:cc_library.bzl", "cc_library")
load("@rules_shell//shell:sh_library.bzl", "sh_library")

cc_library(
    name = "lib_with_non_cc_deps",
    hdrs = ["lib.h"],
    # 'implementation_deps' does not allow targets without CcInfo provider, like 'deps' does
    implementation_deps = [],
    # sh_library is on an allow list for dependencies not offering CcInfo
    deps = [":non_cc_dep"],
)

sh_library(
    name = "non_cc_dep",
)
