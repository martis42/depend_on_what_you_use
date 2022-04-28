load("//:defs.bzl", "dwyu_aspect_factory")

interface_deps_aspect = dwyu_aspect_factory(use_interface_deps = True)
