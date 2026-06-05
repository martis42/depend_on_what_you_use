load("@depend_on_what_you_use//dwyu/cc:defs.bzl", "dwyu_cc_aspect_factory")

map_specific_deps = dwyu_cc_aspect_factory(target_mapping = Label("//target_mapping/mapping:map_specific_deps"))
map_direct_deps = dwyu_cc_aspect_factory(target_mapping = Label("//target_mapping/mapping:map_direct_deps"))
map_transitive_deps = dwyu_cc_aspect_factory(target_mapping = Label("//target_mapping/mapping:map_transitive_deps"))
