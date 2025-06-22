load("@depend_on_what_you_use//src/cc_toolchain_headers:providers.bzl", "DwyuCcToolchainHeadersInfo")

def _custom_cc_toolchain_headers_info_impl(ctx):
    return DwyuCcToolchainHeadersInfo(headers_info = ctx.file._info)

custom_cc_toolchain_headers_info = rule(
    implementation = _custom_cc_toolchain_headers_info_impl,
    provides = [DwyuCcToolchainHeadersInfo],
    attrs = {"_info": attr.label(
        allow_single_file = True,
        default = Label("//ignore_toolchain_headers:custom_ignored_headers.json"),
    )},
)
