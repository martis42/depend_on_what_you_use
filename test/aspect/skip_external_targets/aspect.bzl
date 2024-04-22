load("@depend_on_what_you_use//:defs.bzl", "dwyu_aspect_factory")

dwyu_skip_external = dwyu_aspect_factory(skip_external_targets = True)
