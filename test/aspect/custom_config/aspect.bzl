load("//:defs.bzl", "dwyu_aspect_factory")

ignore_include_paths_aspect = dwyu_aspect_factory(config = "//test/aspect/custom_config:ignore_include_paths.json")
extra_ignore_include_paths_aspect = dwyu_aspect_factory(config = "//test/aspect/custom_config:extra_ignore_include_paths.json")
extra_ignore_include_patterns_aspect = dwyu_aspect_factory(config = "//test/aspect/custom_config:ignore_include_patterns.json")
