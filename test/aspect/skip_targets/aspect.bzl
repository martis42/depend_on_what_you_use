load("@depend_on_what_you_use//dwyu/cc:defs.bzl", "dwyu_cc_aspect_factory")

dwyu_skip_exact = dwyu_cc_aspect_factory(skip_targets = ["//skip_targets:broken_exact"])
dwyu_skip_package = dwyu_cc_aspect_factory(skip_targets = ["//skip_targets/sub:all"])
dwyu_skip_recursive_pattern = dwyu_cc_aspect_factory(skip_targets = ["//skip_targets/sub/..."])
dwyu_skip_in_recursion = dwyu_cc_aspect_factory(recursive = True, skip_targets = ["//skip_targets:middle"])
