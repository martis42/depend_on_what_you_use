load("//:defs.bzl", "dwyu_aspect_factory")

dwyu_custom_tags = dwyu_aspect_factory(skipped_tags = ["tag_marking_skipping"])
