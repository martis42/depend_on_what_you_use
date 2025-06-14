DwyuCcToolchainHeadersInfo = provider(
    "Information about header files which are reachable through a Bazel C/C++ toolchain.",
    fields = {
        "headers_info": "File storing all header file paths relative to the include directories in a list in json format",
    },
)
