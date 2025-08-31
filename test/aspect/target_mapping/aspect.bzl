load("@depend_on_what_you_use//:defs.bzl", "dwyu_aspect_factory")

map_specific_deps = dwyu_aspect_factory(target_mapping = Label("//target_mapping/mapping:map_specific_deps"))
map_direct_deps = dwyu_aspect_factory(target_mapping = Label("//target_mapping/mapping:map_direct_deps"))
map_transitive_deps = dwyu_aspect_factory(target_mapping = Label("//target_mapping/mapping:map_transitive_deps"))

map_specific_deps_cpp = dwyu_aspect_factory(target_mapping = Label("//target_mapping/mapping:map_specific_deps"), use_cpp_implementation = True)
map_direct_deps_cpp = dwyu_aspect_factory(target_mapping = Label("//target_mapping/mapping:map_direct_deps"), use_cpp_implementation = True)
map_transitive_deps_cpp = dwyu_aspect_factory(target_mapping = Label("//target_mapping/mapping:map_transitive_deps"), use_cpp_implementation = True)
