load("@depend_on_what_you_use//dwyu/cc:defs.bzl", "dwyu_cc_aspect_factory")

dwyu_with_priv_hdrs = dwyu_cc_aspect_factory(analysis_ignores_private_headers_from_deps = False)
