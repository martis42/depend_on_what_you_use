load("@depend_on_what_you_use//:defs.bzl", "dwyu_aspect_factory")

dwyu_no_preprocessor = dwyu_aspect_factory(no_preprocessor = True)
