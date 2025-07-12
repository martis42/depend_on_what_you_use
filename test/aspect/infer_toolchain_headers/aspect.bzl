load("@depend_on_what_you_use//:defs.bzl", "dwyu_aspect_factory")

dwyu_infer_headers = dwyu_aspect_factory(ignore_toolchain_headers = True)
