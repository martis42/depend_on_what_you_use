load("@depend_on_what_you_use//dwyu/cc:defs.bzl", "dwyu_cc_aspect_factory")

map_direct_deps_all = dwyu_cc_aspect_factory(target_mapping = Label("//target_mapping/mapping:map_direct_deps_all"))
map_direct_deps_filtered = dwyu_cc_aspect_factory(target_mapping = Label("//target_mapping/mapping:map_direct_deps_filtered"))

map_explicit_deps = dwyu_cc_aspect_factory(target_mapping = Label("//target_mapping/mapping:map_explicit_deps"))

map_transitive_deps_all = dwyu_cc_aspect_factory(target_mapping = Label("//target_mapping/mapping:map_transitive_deps_all"))
map_transitive_deps_filtered = dwyu_cc_aspect_factory(target_mapping = Label("//target_mapping/mapping:map_transitive_deps_filtered"))

# Legacy mapping mode
map_specific_deps = dwyu_cc_aspect_factory(target_mapping = Label("//target_mapping/mapping:map_specific_deps"))

# Legacy syntax (a plain MAP_DIRECT_DEPS/MAP_TRANSITIVE_DEPS token), always mapping all direct/transitive deps.
map_direct_deps_legacy = dwyu_cc_aspect_factory(target_mapping = Label("//target_mapping/mapping:map_direct_deps_legacy"))
map_transitive_deps_legacy = dwyu_cc_aspect_factory(target_mapping = Label("//target_mapping/mapping:map_transitive_deps_legacy"))
