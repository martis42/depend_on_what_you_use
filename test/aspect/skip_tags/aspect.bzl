load("@depend_on_what_you_use//:defs.bzl", "dwyu_cc_aspect_factory")

dwyu_custom_tags = dwyu_cc_aspect_factory(skipped_tags = ["tag_marking_skipping"])
