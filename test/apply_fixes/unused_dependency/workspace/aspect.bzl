load("@depend_on_what_you_use//:defs.bzl", "dwyu_aspect_factory")

default_aspect = dwyu_aspect_factory()
optimizes_impl_deps_aspect = dwyu_aspect_factory(analysis_optimizes_impl_deps = True)
