load("@depend_on_what_you_use//:defs.bzl", "dwyu_cc_aspect_factory")

dwyu_fast = dwyu_cc_aspect_factory(preprocessing_mode = "fast")
dwyu_ignore_system_includes = dwyu_cc_aspect_factory(preprocessing_mode = "ignore_system_includes")
