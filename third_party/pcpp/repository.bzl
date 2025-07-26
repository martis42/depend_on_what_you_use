load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

def pcpp():
    http_archive(
        name = "dwyu_pcpp",
        sha256 = "5af9fbce55f136d7931ae915fae03c34030a3b36c496e72d9636cedc8e2543a1",
        strip_prefix = "pcpp-1.30",
        build_file = Label("//third_party/pcpp:pcpp.BUILD"),
        urls = [
            "https://files.pythonhosted.org/packages/41/07/876153f611f2c610bdb8f706a5ab560d888c938ea9ea65ed18c374a9014a/pcpp-1.30.tar.gz",
        ],
        patches = [
            # Tested for 'cuda.h' by reporter of https://github.com/martis42/depend_on_what_you_use/issues/300
            # Corresponding pcpp issue: https://github.com/ned14/pcpp/issues/72
            # We tested that this patch resolves pcpp issue #72 and all pcpp unit test remain green.
            # pcpp will hopefully see development again in 2025 and then we should be able to drop this patch.
            Label("//third_party/pcpp:recursion_fix.patch"),
        ],
    )
