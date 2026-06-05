load("//:defs.bzl", "dwyu_cc_aspect_factory")

dwyu = dwyu_cc_aspect_factory(analysis_optimizes_impl_deps = True)
