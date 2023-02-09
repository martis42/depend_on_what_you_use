load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")
load("@bazel_tools//tools/build_defs/repo:utils.bzl", "maybe")

def _clean_dep(dep):
    return str(Label(dep))

def public_dependencies():
    version = "0.10.0"

    # NOTE(storypku):
    # The pip_parse_vendored mechanism used by //third_party:vendor_requirements
    # was first introduced in rules_python 0.8.1.
    # However, we have to bump rules_python to 0.10.0+ (which drops support for Python < 3.7)
    # to avoid the following error when running DWYU:
    # ```
    # ModuleNotFoundError: No module named 'clang'
    # ```
    maybe(
        http_archive,
        name = "rules_python",
        strip_prefix = "rules_python-{version}".format(version = version),
        sha256 = "56dc7569e5dd149e576941bdb67a57e19cd2a7a63cc352b62ac047732008d7e1",
        urls = ["https://github.com/bazelbuild/rules_python/archive/{version}.tar.gz".format(version = version)],
        patch_args = ["-p1"],
        patches = [
            _clean_dep("//third_party/rules_python:p01_deprecate_to_json.patch"),
        ],
    )

def private_dependencies():
    http_archive(
        name = "bazel_skylib",
        sha256 = "f7be3474d42aae265405a592bb7da8e171919d74c16f082a5457840f06054728",
        urls = ["https://github.com/bazelbuild/bazel-skylib/releases/download/1.2.1/bazel-skylib-1.2.1.tar.gz"],
    )
