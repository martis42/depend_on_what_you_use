load("//dwyu/cc_toolchain_headers/private:gather_cc_toolchain_headers.bzl", _gather_cc_toolchain_headers = "gather_cc_toolchain_headers")

visibility("//dwyu/...")

dwyu_gather_cc_toolchain_headers = _gather_cc_toolchain_headers
