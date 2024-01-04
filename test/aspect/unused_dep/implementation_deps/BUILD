# This has to be a separate BUILD file, since otherwise tests for Bazel version < 5.0.0 fails to parse the BUILD
# for for the other tests.

cc_library(
    name = "implementation_deps_lib",
    srcs = ["//unused_dep:using_bar"],
    implementation_deps = [
        "//unused_dep:bar",
        "//unused_dep:foo",
    ],
)
