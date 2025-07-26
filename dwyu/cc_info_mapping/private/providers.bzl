visibility("//dwyu/cc_info_mapping/...")

DwyuRemappedCcInfo = provider(
    "An alternative CcInfo object for a target which can be used by DWYU during the analysis",
    fields = {
        "cc_info": "CcInfo provider",
        "target": "Label of target which should use the cc_info object",
    },
)
