load("@depend_on_what_you_use//:defs.bzl", "dwyu_aspect_factory")

dwyu_recursive = dwyu_aspect_factory(recursive = True)
dwyu_recursive_impl_deps = dwyu_aspect_factory(recursive = True, use_implementation_deps = True)
