load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

def pcpp():
    version = "1.30"
    http_archive(
        name = "dwyu_pcpp",
        sha256 = "5af9fbce55f136d7931ae915fae03c34030a3b36c496e72d9636cedc8e2543a1",
        strip_prefix = "pcpp-{}".format(version),
        build_file = "@depend_on_what_you_use//third_party/pcpp:pcpp.BUILD",
        urls = [
            "https://files.pythonhosted.org/packages/41/07/876153f611f2c610bdb8f706a5ab560d888c938ea9ea65ed18c374a9014a/pcpp-{v}.tar.gz".format(v = version),
        ],
    )
