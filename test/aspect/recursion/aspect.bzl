load("@depend_on_what_you_use//dwyu/cc:defs.bzl", "dwyu_cc_aspect_factory")

dwyu_recursive = dwyu_cc_aspect_factory(recursive = True)
