load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")
load("@bazel_tools//tools/build_defs/repo:utils.bzl", "maybe")
load("@depend_on_what_you_use//third_party/pcpp:repository.bzl", "pcpp")

def dependencies():
    maybe(
        http_archive,
        name = "rules_python",
        sha256 = "c6fb25d0ba0246f6d5bd820dd0b2e66b339ccc510242fd4956b9a639b548d113",
        strip_prefix = "rules_python-0.37.2",
        urls = ["https://github.com/bazelbuild/rules_python/releases/download/0.37.2/rules_python-0.37.2.tar.gz"],
    )

    maybe(
        http_archive,
        name = "rules_cc",
        sha256 = "f4aadd8387f381033a9ad0500443a52a0cea5f8ad1ede4369d3c614eb7b2682e",
        strip_prefix = "rules_cc-0.0.15",
        urls = ["https://github.com/bazelbuild/rules_cc/releases/download/0.0.15/rules_cc-0.0.15.tar.gz"],
    )

    # rules_cc uses this but does not add it to https://github.com/bazelbuild/rules_cc/blob/0.0.15/cc/repositories.bzl
    maybe(
        http_archive,
        name = "com_google_protobuf",
        sha256 = "da288bf1daa6c04d03a9051781caa52aceb9163586bff9aa6cfb12f69b9395aa",
        strip_prefix = "protobuf-27.0",
        url = "https://github.com/protocolbuffers/protobuf/releases/download/v27.0/protobuf-27.0.tar.gz",
    )

    # Keep in sync with MODULE.bazel
    http_archive(
        name = "bazel_skylib",
        sha256 = "bc283cdfcd526a52c3201279cda4bc298652efa898b10b4db0837dc51652756f",
        urls = ["https://github.com/bazelbuild/bazel-skylib/releases/download/1.7.1/bazel-skylib-1.7.1.tar.gz"],
    )

    pcpp()
