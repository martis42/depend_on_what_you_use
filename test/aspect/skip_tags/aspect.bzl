load("//:defs.bzl", "dwyu_aspect_factory")

test_aspect = dwyu_aspect_factory(skipped_tags = ["tag_marking_skipping"])
