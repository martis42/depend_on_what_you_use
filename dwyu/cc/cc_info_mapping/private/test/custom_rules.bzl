load("@rules_cc//cc/common:cc_common.bzl", "cc_common")
load("@rules_cc//cc/common:cc_info.bzl", "CcInfo")

visibility("//dwyu/cc/cc_info_mapping/...")

def _cc_info_with_custom_deps_impl(ctx):
    """Provide CcInfo containing only the headers of this target, deliberately not merging the CcInfo of any dependency.
    We ignore the CcInfo provider of any dependency attribute to prove our mapping makes them available and not the implementation of this rule.
    """
    return [CcInfo(compilation_context = cc_common.create_compilation_context(headers = depset(ctx.files.hdrs)))]

# Minimal custom rule that provides CcInfo and depends on other CC targets, but deliberately has no "deps" attribute
cc_info_with_custom_deps = rule(
    implementation = _cc_info_with_custom_deps_impl,
    provides = [CcInfo],
    attrs = {
        "hdrs": attr.label_list(allow_files = [".h"]),
        "multiple_deps": attr.label_list(providers = [CcInfo]),
        "non_cc_label_attr": attr.label(
            allow_files = True,
            doc = "Label attribute whose target does not provide CcInfo. Prove we automatically ignore label attributes not providing CcInfo",
        ),
        "non_target_attr": attr.string(default = "Prove we automatically ignore attributes not providing CcInfo"),
        "non_target_list_attr": attr.string_list(default = ["Prove", "we", "automatically", "ignore", "attributes", "not", "providing", "CcInfo"]),
        "single_dep": attr.label(providers = [CcInfo]),
    },
)
