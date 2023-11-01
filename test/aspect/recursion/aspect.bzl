load("//:defs.bzl", "dwyu_aspect_factory")

recursive_aspect = dwyu_aspect_factory(recursive = True)
recursive_impl_deps_aspect = dwyu_aspect_factory(recursive = True, use_implementation_deps = True)
