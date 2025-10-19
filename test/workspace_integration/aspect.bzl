load("@custom_dwyu//:defs.bzl", "dwyu_aspect_factory")

dwyu = dwyu_aspect_factory()
dwyu_cpp = dwyu_aspect_factory(use_cpp_implementation = True)
