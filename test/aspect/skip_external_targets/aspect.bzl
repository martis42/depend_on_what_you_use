load("@depend_on_what_you_use//dwyu/cc:defs.bzl", "dwyu_cc_aspect_factory")

dwyu_skip_external = dwyu_cc_aspect_factory(skip_external_targets = True)
