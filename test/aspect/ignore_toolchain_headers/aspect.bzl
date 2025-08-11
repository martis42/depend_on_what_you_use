load("@depend_on_what_you_use//:defs.bzl", "dwyu_aspect_factory")

dwyu_ignore_toolchain_headers = dwyu_aspect_factory(ignore_cc_toolchain_headers = True)
dwyu_custom_toolchain_headers_info = dwyu_aspect_factory(ignore_cc_toolchain_headers = True, cc_toolchain_headers_info = Label("//ignore_toolchain_headers:custom_cc_toolchain_headers_info"))

dwyu_ignore_toolchain_headers_cct = dwyu_aspect_factory(ignore_cc_toolchain_headers = True, use_cc_toolchain_preprocessor = True)
dwyu_custom_toolchain_headers_info_cct = dwyu_aspect_factory(ignore_cc_toolchain_headers = True, cc_toolchain_headers_info = Label("//ignore_toolchain_headers:custom_cc_toolchain_headers_info"), use_cc_toolchain_preprocessor = True)
