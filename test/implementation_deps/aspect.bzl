load("//:defs.bzl", "dwyu_aspect_factory")

implementation_deps_aspect = dwyu_aspect_factory(use_implementation_deps = True)
