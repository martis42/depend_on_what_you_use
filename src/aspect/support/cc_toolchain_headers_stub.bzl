load("//src/cc_toolchain_headers:providers.bzl", "DwyuCcToolchainHeadersInfo")

visibility("//src/aspect/...")

def _cc_toolchain_headers_stub_impl(ctx):
    return DwyuCcToolchainHeadersInfo(headers_info = ctx.file._info)

cc_toolchain_headers_stub = rule(
    implementation = _cc_toolchain_headers_stub_impl,
    provides = [DwyuCcToolchainHeadersInfo],
    attrs = {"_info": attr.label(
        allow_single_file = True,
        default = Label("//src/aspect/support:cc_toolchain_headers_info_stub.json"),
    )},
    doc = "Stub target doing nothing so the DWYU aspect does not needlessly try to analyze the CC toolchain if the user sets 'ignore_cc_toolchain_headers' to False",
)
