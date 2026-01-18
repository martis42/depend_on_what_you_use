load("@depend_on_what_you_use//:defs.bzl", "dwyu_aspect_factory")

# Some DWYU flags can be controlled via '--aspects_parameters'. Those have to set explicitly. Either in the factory
# creating the aspect used by the rule, or in the attrs of the rule using the aspect, see rule_using_dwyu/rule.bzl.
dwyu = dwyu_aspect_factory(analysis_optimizes_impl_deps = True)

dwyu_recursive = dwyu_aspect_factory(recursive = True)
dwyu_recursive_skip_external = dwyu_aspect_factory(recursive = True, skip_external_targets = True)
dwyu_custom_skipping = dwyu_aspect_factory(skipped_tags = ["my_tag"])
dwyu_set_cplusplus = dwyu_aspect_factory(experimental_set_cplusplus = True)

# We need to explicitly pass labels as passing strings does not work with a bzlmod setup.
dwyu_ignoring_includes = dwyu_aspect_factory(ignored_includes = Label("@//ignoring_includes:ignore_includes.json"))
dwyu_map_specific_deps = dwyu_aspect_factory(target_mapping = Label("@//target_mapping/mapping:map_specific_deps"))
dwyu_map_direct_deps = dwyu_aspect_factory(target_mapping = Label("@//target_mapping/mapping:map_direct_deps"))
dwyu_map_transitive_deps = dwyu_aspect_factory(target_mapping = Label("@//target_mapping/mapping:map_transitive_deps"))
