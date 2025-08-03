load("@depend_on_what_you_use//:defs.bzl", "dwyu_aspect_factory")

dwyu_legacy_default = dwyu_aspect_factory()
dwyu_cc_toolchain = dwyu_aspect_factory(use_cc_toolchain_preprocessor = True)
