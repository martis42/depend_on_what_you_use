load("@depend_on_what_you_use//:defs.bzl", "dwyu_aspect_factory")

dwyu = dwyu_aspect_factory()
dwyu_pp_no_system_includes = dwyu_aspect_factory(preprocessing_mode = "ignore_system_includes")
dwyu_pp_fast = dwyu_aspect_factory(preprocessing_mode = "fast")
