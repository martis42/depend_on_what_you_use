load("//:defs.bzl", "dwyu_aspect_factory")

ignore_include_paths_aspect = dwyu_aspect_factory(ignored_includes = Label("//test/aspect/ignore_includes:ignore_include_paths.json"))
extra_ignore_include_paths_aspect = dwyu_aspect_factory(ignored_includes = Label("//test/aspect/ignore_includes:extra_ignore_include_paths.json"))
extra_ignore_include_patterns_aspect = dwyu_aspect_factory(ignored_includes = Label("//test/aspect/ignore_includes:ignore_include_patterns.json"))
