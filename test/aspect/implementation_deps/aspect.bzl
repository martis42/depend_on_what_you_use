load("@depend_on_what_you_use//dwyu/cc:defs.bzl", "dwyu_cc_aspect_factory")

optimize_impl_deps = dwyu_cc_aspect_factory(analysis_optimizes_impl_deps = True)
