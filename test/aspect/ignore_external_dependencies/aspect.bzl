load("@depend_on_what_you_use//dwyu/cc:defs.bzl", "dwyu_cc_aspect_factory")

ignore_external = dwyu_cc_aspect_factory(ignore_external_dependencies = True)
ignore_external_optimizing_impl_deps = dwyu_cc_aspect_factory(ignore_external_dependencies = True, analysis_optimizes_impl_deps = True)
