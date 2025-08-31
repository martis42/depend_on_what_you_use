load("@depend_on_what_you_use//:defs.bzl", "dwyu_aspect_factory")

dwyu = dwyu_aspect_factory()
dwyu_impl_deps = dwyu_aspect_factory(use_implementation_deps = True)

dwyu_cpp = dwyu_aspect_factory(use_cpp_implementation = True)
dwyu_impl_deps_cpp = dwyu_aspect_factory(use_implementation_deps = True, use_cpp_implementation = True)
