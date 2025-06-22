load("//src/cc_toolchain_headers/private:gather_cc_toolchain_headers.bzl", _gather_cc_toolchain_headers = "gather_cc_toolchain_headers")

visibility("//src/...")

dwyu_gather_cc_toolchain_headers = _gather_cc_toolchain_headers
