load("@bazel_skylib//rules:diff_test.bzl", "diff_test")
load("@bazel_skylib//rules:write_file.bzl", "write_file")

# NOTE(storypku):
# compile_pip_requirements was disabled for [issue](https://github.com/bazelbuild/rules_python/issues/497)
#
# ```
# load("@rules_python//python:pip.bzl", "compile_pip_requirements")
# # This rule adds a convenient way to update the requirements file.
# # To run: `bazel run //third_party:requirements.update`
# compile_pip_requirements(
#    name = "requirements",
#    requirements_in = "requirements.in",
#    requirements_txt = "requirements.txt",
# )
# ```
genrule(
    name = "clean_requirements",
    srcs = ["@dwyu_py_deps//:requirements.bzl"],
    outs = ["requirements.clean.bzl"],
    cmd = """ cat $< | tr "'" '"' > $@ """,
)

write_file(
    name = "generate_update_requirements_sh",
    out = "update_requirements.sh",
    content = [
        "#!/usr/bin/env bash",
        "cd $BUILD_WORKSPACE_DIRECTORY",
        "cp -fv bazel-bin/third_party/requirements.clean.bzl requirements.bzl",
    ],
)

sh_binary(
    name = "vendor_requirements",
    srcs = ["update_requirements.sh"],
    data = [":clean_requirements"],
)

# Ensures that the requirements.bzl file is updated based on the requirements.txt lockfile.
diff_test(
    name = "test_vendored_requirements",
    failure_message = """Please run: "bazel run //third_party:vendor_requirements" """,
    file1 = "//:requirements.bzl",
    file2 = ":clean_requirements",
)
