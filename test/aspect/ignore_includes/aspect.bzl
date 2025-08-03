load("@depend_on_what_you_use//:defs.bzl", "dwyu_aspect_factory")

ignore_include_paths_aspect = dwyu_aspect_factory(ignored_includes = Label("//ignore_includes:ignore_include_paths.json"))
extra_ignore_include_paths_aspect = dwyu_aspect_factory(ignored_includes = Label("//ignore_includes:extra_ignore_include_paths.json"))
extra_ignore_include_patterns_aspect = dwyu_aspect_factory(ignored_includes = Label("//ignore_includes:ignore_include_patterns.json"))

ignore_include_paths_aspect_cct = dwyu_aspect_factory(ignored_includes = Label("//ignore_includes:ignore_include_paths.json"), use_cc_toolchain_preprocessor = True)
extra_ignore_include_paths_aspect_cct = dwyu_aspect_factory(ignored_includes = Label("//ignore_includes:extra_ignore_include_paths.json"), use_cc_toolchain_preprocessor = True)
extra_ignore_include_patterns_aspect_cct = dwyu_aspect_factory(ignored_includes = Label("//ignore_includes:ignore_include_patterns.json"), use_cc_toolchain_preprocessor = True)
