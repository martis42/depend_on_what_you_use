load("@rules_python//python:py_test.bzl", "py_test")

py_test(
    name = "release_prep_test",
    srcs = ["release_prep_test.py"],
    deps = ["//.github/scripts:release_prep"],
)

py_test(
    name = "release_finalize_test",
    srcs = ["release_finalize_test.py"],
    deps = [
        "//.github/scripts:release_finalize",
        "//.github/scripts:release_prep",
    ],
)
