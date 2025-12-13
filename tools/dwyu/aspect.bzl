load("//:defs.bzl", "dwyu_aspect_factory")

dwyu = dwyu_aspect_factory(use_cpp_implementation = True, use_implementation_deps = True)
