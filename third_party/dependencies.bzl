load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")
load("@bazel_tools//tools/build_defs/repo:utils.bzl", "maybe")
load("@depend_on_what_you_use//third_party/pcpp:repository.bzl", "pcpp")

def dependencies():
    # Keep in sync with MODULE.bazel
    rules_python_version = "0.28.0"
    maybe(
        http_archive,
        name = "rules_python",
        sha256 = "d70cd72a7a4880f0000a6346253414825c19cdd40a28289bdf67b8e6480edff8",
        strip_prefix = "rules_python-{}".format(rules_python_version),
        urls = ["https://github.com/bazelbuild/rules_python/releases/download/{v}/rules_python-{v}.tar.gz".format(v = rules_python_version)],
    )

    # Keep in sync with MODULE.bazel
    rules_cc_version = "0.0.9"
    maybe(
        http_archive,
        name = "rules_cc",
        sha256 = "2037875b9a4456dce4a79d112a8ae885bbc4aad968e6587dca6e64f3a0900cdf",
        strip_prefix = "rules_cc-{}".format(rules_cc_version),
        urls = ["https://github.com/bazelbuild/rules_cc/releases/download/{v}/rules_cc-{v}.tar.gz".format(v = rules_cc_version)],
    )

    # Keep in sync with MODULE.bazel
    skylib_version = "1.5.0"
    http_archive(
        name = "bazel_skylib",
        sha256 = "cd55a062e763b9349921f0f5db8c3933288dc8ba4f76dd9416aac68acee3cb94",
        urls = ["https://github.com/bazelbuild/bazel-skylib/releases/download/{v}/bazel-skylib-{v}.tar.gz".format(v = skylib_version)],
    )

    pcpp()
