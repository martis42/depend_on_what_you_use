load("@rules_cc//cc/common:cc_common.bzl", "cc_common")
load("@rules_cc//cc/common:cc_info.bzl", "CcInfo")

visibility("//dwyu/cc/cc_info_mapping/...")

def _cc_info_without_deps_impl(ctx):
    compilation_context = cc_common.create_compilation_context(
        headers = depset(ctx.files.hdrs),
    )
    return [CcInfo(compilation_context = compilation_context)]

# Minimal custom rule that provides CcInfo but deliberately has no "deps" attribute,
# simulating a real-world rule that is unaware of the canonical "deps" attribute.
cc_info_without_deps = rule(
    implementation = _cc_info_without_deps_impl,
    provides = [CcInfo],
    attrs = {
        "hdrs": attr.label_list(allow_files = [".h"]),
    },
)
