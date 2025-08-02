load("//:defs.bzl", "dwyu_aspect_factory")

dwyu = dwyu_aspect_factory(use_cc_toolchain_preprocessor = True)
