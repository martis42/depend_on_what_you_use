visibility("public")

DwyuCcToolchainHeadersInfo = provider(
    "Information about header files which can be included without any explicit dependency through the CC toolchain.",
    fields = {
        "headers_info": "File storing all header file include paths usable through the CC toolchain. File content is a list in json format.",
    },
)
