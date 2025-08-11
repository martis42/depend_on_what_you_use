load("@depend_on_what_you_use//:defs.bzl", "dwyu_aspect_factory")

dwyu_custom_tags = dwyu_aspect_factory(skipped_tags = ["tag_marking_skipping"])

dwyu_custom_tags_cct = dwyu_aspect_factory(skipped_tags = ["tag_marking_skipping"], use_cc_toolchain_preprocessor = True)
