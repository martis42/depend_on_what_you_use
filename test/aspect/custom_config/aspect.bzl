load("//:defs.bzl", "dwyu_aspect_factory")

full_custom_config_aspect = dwyu_aspect_factory(config = "//test/aspect/custom_config:full_custom_config.json")
ignore_include_paths_aspect = dwyu_aspect_factory(config = "//test/aspect/custom_config:ignore_include_paths.json")
extra_ignore_include_paths_aspect = dwyu_aspect_factory(config = "//test/aspect/custom_config:extra_ignore_include_paths.json")
