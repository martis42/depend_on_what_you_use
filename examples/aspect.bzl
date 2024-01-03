load("@depend_on_what_you_use//:defs.bzl", "dwyu_aspect_factory")

dwyu = dwyu_aspect_factory(use_implementation_deps = True)

dwyu_recursive = dwyu_aspect_factory(recursive = True)
dwyu_custom_skipping = dwyu_aspect_factory(skipped_tags = ["my_tag"])

# We need to explicitly pass labels as passing strings does not work with a bzlmod setup.
dwyu_ignoring_includes = dwyu_aspect_factory(ignored_includes = Label("@//ignoring_includes:ignore_includes.json"))
dwyu_map_specific_deps = dwyu_aspect_factory(target_mapping = Label("@//target_mapping/mapping:map_specific_deps"))
dwyu_map_direct_deps = dwyu_aspect_factory(target_mapping = Label("@//target_mapping/mapping:map_direct_deps"))
dwyu_map_transitive_deps = dwyu_aspect_factory(target_mapping = Label("@//target_mapping/mapping:map_transitive_deps"))
