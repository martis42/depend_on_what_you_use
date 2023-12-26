load("//src/aspect:factory.bzl", _dwyu_aspect_factory = "dwyu_aspect_factory")
load(
    "//src/cc_info_mapping:cc_info_mapping.bzl",
    _MAP_DIRECT_DEPS = "MAP_DIRECT_DEPS",
    _MAP_TRANSITIVE_DEPS = "MAP_TRANSITIVE_DEPS",
    _dwyu_make_cc_info_mapping = "dwyu_make_cc_info_mapping",
)

dwyu_aspect_factory = _dwyu_aspect_factory

dwyu_make_cc_info_mapping = _dwyu_make_cc_info_mapping
MAP_DIRECT_DEPS = _MAP_DIRECT_DEPS
MAP_TRANSITIVE_DEPS = _MAP_TRANSITIVE_DEPS
