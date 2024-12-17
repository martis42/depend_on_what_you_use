def label_to_name(label):
    """
    Create a legal name from a string describing a Bazel target label
    """
    return str(label).replace("@", "").replace("//", "_").replace("/", "_").replace(":", "_")

def print_compilation_context(cc_info, headline = None):
    """
    Print CcInfo's compilation_context in a structured way.

    Debugging is eased by those flags which prevent print statements being omitted on subsequent execution:
    --nokeep_state_after_build
    --notrack_incremental_state

    Args:
        cc_info: A CompilationContext object
        headline: Optional context information displayed before the CompilationContext information
    """
    cc = cc_info.compilation_context
    headline_str = "\n" + headline if headline else ""
    external_includes = cc.external_includes if hasattr(cc, "external_includes") else "NA"
    print("""{headline}
  defines                : {d}
  local_defines          : {ld}
  headers                : {h}
  direct_headers         : {dh}
  direct_private_headers : {d_priv_h}
  direct_public_headers  : {d_pub_h}
  direct_textual_headers : {dth}
  includes               : {i}
  framework_includes     : {fi}
  quote_includes         : {qi}
  external_includes      : {ei}
  system_includes        : {si}
    """.rstrip().format(
        headline = headline_str,
        d = cc.defines,
        dh = cc.direct_headers,
        d_priv_h = cc.direct_private_headers,
        d_pub_h = cc.direct_public_headers,
        dth = cc.direct_textual_headers,
        fi = cc.framework_includes,
        h = cc.headers,
        i = cc.includes,
        ld = cc.local_defines,
        qi = cc.quote_includes,
        ei = external_includes,
        si = cc.system_includes,
    ))
