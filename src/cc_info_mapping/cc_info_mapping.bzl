load("@depend_on_what_you_use//src/cc_info_mapping/private:direct_deps.bzl", "mapping_to_direct_deps")
load("@depend_on_what_you_use//src/cc_info_mapping/private:explicit.bzl", "explicit_mapping")
load("@depend_on_what_you_use//src/cc_info_mapping/private:providers.bzl", "DwyuCcInfoRemapInfo")
load("@depend_on_what_you_use//src/cc_info_mapping/private:transitive_deps.bzl", "mapping_to_transitive_deps")
load("@depend_on_what_you_use//src/utils:utils.bzl", "label_to_name")

MAP_DIRECT_DEPS = "__DWYU_MAP_DIRECT_DEPS__"
MAP_TRANSITIVE_DEPS = "__DWYU_MAP_TRANSITIVE_DEPS__"

DwyuCcInfoRemappingsInfo = provider(
    "Dictionary of targets labels wnd which CcInfo provider DWYU should use for analysing them",
    fields = {
        "mapping": "Dictionary with structure {'target label': CcInfo provider which should be used by DWYU}",
    },
)

def _make_remapping_info_impl(ctx):
    return DwyuCcInfoRemappingsInfo(mapping = {
        remap[DwyuCcInfoRemapInfo].target: remap[DwyuCcInfoRemapInfo].cc_info
        for remap in ctx.attr.remappings
    })

_make_remapping_info = rule(
    implementation = _make_remapping_info_impl,
    provides = [DwyuCcInfoRemappingsInfo],
    attrs = {
        "remappings": attr.label_list(providers = [DwyuCcInfoRemapInfo]),
    },
)

def dwyu_make_cc_info_mapping(name, mapping):
    """
    Create a mapping which allows treating targets as if they themselves would offer header files, which in fact are
    coming from their dependencies. This enables the DWYU analysis to skip over some usage of headers provided by
    transitive dependencies without raising an error.

    Args:
        name: Unique name for this target. Will be the prefix for all private intermediate targets.
        mapping: Dictionary containing various targets and how they should be mapped. Possible mappings are:
                 - An explicit list of targets which are mapped to the main target. Be careful only to choose targets
                   which are dependencies of the main target!
                 - The MAP_DIRECT_DEPS token which tells the rule to map all direct dependencies to the main target.
                 - The MAP_TRANSITIVE_DEPS token which tells the rule to map recursively all transitive dependencies to
                   the main target.
    """
    mappings = []
    for target, map_to in mapping.items():
        mapping_action = "{}_mapping_{}".format(name, label_to_name(target))
        if map_to == MAP_DIRECT_DEPS:
            mapping_to_direct_deps(
                name = mapping_action,
                target = target,
            )
        elif map_to == MAP_TRANSITIVE_DEPS:
            mapping_to_transitive_deps(
                name = mapping_action,
                target = target,
            )
        else:
            explicit_mapping(
                name = mapping_action,
                target = target,
                map_to = map_to,
            )
        mappings.append(mapping_action)

    _make_remapping_info(
        name = name,
        remappings = mappings,
    )
