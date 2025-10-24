load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")
load("@bazel_tools//tools/build_defs/repo:utils.bzl", "maybe")

def xz():
    maybe(
        http_archive,
        name = "xz",
        sha256 = "135c90b934aee8fbc0d467de87a05cb70d627da36abe518c357a873709e5b7d6",
        strip_prefix = "xz-5.4.5",
        urls = ["https://github.com/tukaani-project/xz/releases/download/v5.4.5/xz-5.4.5.tar.gz"],
        patches = [Label("//third_party/xz:bazelization.patch")],
        patch_args = ["-p1"],
    )
