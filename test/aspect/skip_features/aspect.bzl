load("@depend_on_what_you_use//:defs.bzl", "dwyu_aspect_factory")

dwyu_skip_features = dwyu_aspect_factory(skip_features = ["dbg", "-fastbuild"])
