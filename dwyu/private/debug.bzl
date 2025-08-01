"""
Utility functions for debugging. Those shall not be used in production code.
"""

visibility("//dwyu/...")

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

    # buildifier: disable=print
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

def print_cc_toolchain(cc_toolchain):
    """
    Print CcToolchainInfo which is most relevant for us in a structured way.

    Debugging is eased by those flags which prevent print statements being omitted on subsequent execution:
    --nokeep_state_after_build
    --notrack_incremental_state

    Args:
        cc_toolchain: A CcToolchainInfo object
    """

    include_directories = "\n".join(["    {}".format(id) for id in cc_toolchain.built_in_include_directories])
    if include_directories:
        include_directories = "\n" + include_directories

    # buildifier: disable=print
    print(
        """
  toolchain_id                 : {id}
  cpu                          : {cpu}
  compiler                     : {compiler}
  built_in_include_directories : {include_dirs}
  sysroot                      : {root}
  libc                         : {libc}
  compiler_executable          : {ce}
    """.rstrip().format(
            id = cc_toolchain.toolchain_id,
            cpu = cc_toolchain.cpu,
            compiler = cc_toolchain.compiler,
            ce = cc_toolchain.compiler_executable,
            include_dirs = include_directories,
            root = cc_toolchain.sysroot,
            libc = cc_toolchain.libc,
        ),
    )
