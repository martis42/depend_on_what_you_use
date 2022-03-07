load("//:defs.bzl", "dwyu_aspect_factory")

custom_config_aspect = dwyu_aspect_factory(config = "//test/custom_config")
