load("@depend_on_what_you_use//:defs.bzl", "dwyu_aspect_factory")

dwyu = dwyu_aspect_factory(ignore_cc_toolchain_headers = True, use_cpp_implementation = True)
