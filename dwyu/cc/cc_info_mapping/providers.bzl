DwyuCcInfoMappingInfo = provider(
    "Mapping of targets to CcInfo providers which DWYU should use for analysis instead of the targets original CcInfo.",
    fields = {
        "mapping": "Dictionary with structure {'target label': CcInfo}",
    },
)

DwyuRemappedCcInfo = provider(
    """An alternative CcInfo object for a target which can be used by DWYU during the analysis.

The replacement should include the target's own compilation context as well as the information from the compilation contexts selected by the custom mapping algorithm.
The linking info is not used and can be skipped.
""",
    fields = {
        "cc_info": "Replacement CcInfo provider.",
        "target": "Label of the target whose CcInfo should be replaced.",
    },
)
