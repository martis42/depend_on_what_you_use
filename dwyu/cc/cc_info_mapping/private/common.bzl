"""
Shared code private to this package.
"""

load("@rules_cc//cc/common:cc_common.bzl", "cc_common")
load("@rules_cc//cc/common:cc_info.bzl", "CcInfo")
load(":providers.bzl", "DwyuRemappedCcInfo")

visibility("//dwyu/cc/cc_info_mapping/private/...")

DwyuDirectDepsCcInfo = provider(
    "Compilation contexts of direct dependencies, to be filtered and merged by the rule using the aspect.",
    fields = {
        "deps_to_compilation_context": "Dictionary mapping the Label of a direct dependency to its CcInfo.compilation_context",
    },
)

DwyuTransitiveDepsCcInfo = provider(
    "Compilation contexts of dependencies, to be filtered and merged by the rule using the aspect.",
    fields = {
        "compilation_context": "Compilation context provided by this target, which has all compilation contexts from the transitive dependencies merged in.",
        "deps_to_compilation_context": "Dictionary mapping the Label of a direct dependency to its CcInfo.compilation_context. All transitive dependencies of this dependency are merged into this compilation_context.",
    },
)

def cc_info_deps_from_all_attrs(rule_attrs, skip_impl_deps = True):
    """
    Collect all targets found in the rule's attributes.
    By default we ignore implementation_deps since headers provided by them shall by design not be used by consumers of the target.

    Args:
        rule_attrs: The attributes of the rule to inspect.
        skip_impl_deps: Whether to ignore the implementation_deps attribute.

    Returns:
        A list of all dependency targets found in the rule attributes, excluding implementation_deps if skip_impl_deps is set.
    """
    dependencies = []
    for attr_name in dir(rule_attrs):
        if attr_name == "implementation_deps" and skip_impl_deps:
            continue
        attr_value = getattr(rule_attrs, attr_name)
        if type(attr_value) == "Target":
            dependencies.append(attr_value)
        elif type(attr_value) == "list":
            dependencies.extend([dependency for dependency in attr_value if type(dependency) == "Target"])
    return dependencies

def create_remapped_cc_info(target, mapped_compilation_contexts):
    """
    Create a DwyuRemappedCcInfo for 'target' with the given compilation contexts merged into the target's own.
    """
    target_cc_info = target[CcInfo]
    return DwyuRemappedCcInfo(
        target = target.label,
        cc_info = CcInfo(
            compilation_context = cc_common.merge_compilation_contexts(
                compilation_contexts = [target_cc_info.compilation_context] + mapped_compilation_contexts,
            ),
            linking_context = target_cc_info.linking_context,
        ),
    )

def filter_compilation_contexts(deps_to_compilation_context, label_filter):
    """
    Select compilation contexts of dependencies.
    An empty filter selects all dependencies.
    """
    return [
        compilation_context
        for label, compilation_context in deps_to_compilation_context.items()
        if not label_filter or str(label) in label_filter
    ]
