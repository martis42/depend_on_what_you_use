load("@rules_python//python:py_binary.bzl", "py_binary")
load("//dwyu/cc_toolchain_headers:cc_toolchain_headers.bzl", "dwyu_gather_cc_toolchain_headers")
load(":cc_toolchain_headers_stub.bzl", "cc_toolchain_headers_stub")

dwyu_gather_cc_toolchain_headers(
    name = "cc_toolchain_headers",
    visibility = ["//visibility:public"],
)

cc_toolchain_headers_stub(
    name = "cc_toolchain_headers_stub",
    visibility = ["//visibility:public"],
)

py_binary(
    name = "parse_preprocessor_output",
    srcs = ["parse_gcc_like_preprocessor_output.py"],
    # Compatibility to --noexperimental_python_import_all_repositories
    imports = ["../../.."],
    legacy_create_init = False,
    main = "parse_gcc_like_preprocessor_output.py",
    visibility = ["//visibility:public"],
    # TODO make lib target
    deps = ["//dwyu/cc_toolchain_headers/private:gather_cc_toolchain_headers_tool"],
)

py_binary(
    name = "process_target",
    srcs = ["process_target.py"],
    visibility = ["//visibility:public"],
)
