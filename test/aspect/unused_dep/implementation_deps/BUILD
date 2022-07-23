# This has to be a separate BUILD file, since otherwise tests for Bazel version < 5.0.0 fails to parse the BUILD
# for for the other tests.

cc_library(
    name = "implementation_deps_lib",
    srcs = ["//test/aspect/unused_dep:using_bar"],
    implementation_deps = [
        "//test/aspect/unused_dep:bar",
        "//test/aspect/unused_dep:foo",
    ],
)
