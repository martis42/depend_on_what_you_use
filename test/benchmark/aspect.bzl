load("@depend_on_what_you_use//:defs.bzl", "dwyu_aspect_factory")

dwyu_legacy_default = dwyu_aspect_factory()
dwyu_cpp_impl = dwyu_aspect_factory(use_cpp_implementation = True)
