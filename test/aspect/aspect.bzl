load("//:defs.bzl", "dwyu_aspect_factory")

dwyu = dwyu_aspect_factory()
dwyu_impl_deps = dwyu_aspect_factory(use_implementation_deps = True)
