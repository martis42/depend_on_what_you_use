load("@depend_on_what_you_use//dwyu/cc:defs.bzl", "dwyu_cc_aspect_factory")
load("//dwyu_fix:fix_aspect.bzl", "dwyu_fix_aspect_factory")

dwyu = dwyu_cc_aspect_factory()

dwyu_fix = dwyu_fix_aspect_factory(dwyu)
