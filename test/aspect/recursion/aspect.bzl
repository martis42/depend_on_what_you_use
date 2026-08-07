load("@depend_on_what_you_use//dwyu/cc:defs.bzl", "dwyu_cc_aspect_factory")

dwyu_recursive = dwyu_cc_aspect_factory(recursive = True)
dwyu_recursive_stop_on_skip = dwyu_cc_aspect_factory(recursive = True, recursion_stops_on_skip = True, skip_tags = ["custom_skip_tag"], skip_targets = ["//recursion:b"])
