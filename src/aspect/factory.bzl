load(":dwyu.bzl", "dwyu_aspect_impl")

def dwyu_aspect_factory(
        config = Label("@depend_on_what_you_use//src/aspect:private/dwyu_empty_config.json"),
        recursive = False,
        use_implementation_deps = False,
        use_interface_deps = False):
    """
    Create a "Depend on What You Use" (DWYU) aspect.

    An aspect can only have default values and cannot be configured on the command line. Use this factory to create
    an aspect with the desired behavior and then use it on the command line or in rules.

    Args:
        config: Configuration file for the tool comparing the include statements to the dependencies.
        recursive: If true, execute the aspect on all trannsitive dependencies.
                   If false, analyze only the target the aspect is being executed on.
        use_implementation_deps: If true, ensure cc_library dependencies which are used only in private files are
                                 listed in implementation_deps. Only available for Bazel >= 5.0.0 and if flag
                                 '--experimental_cc_implementation_deps' is provided.
        use_interface_deps: If true, ensure cc_library dependencies which are used only in private files are listed in
                            deps and dependencies used in public files are listed in interface_deps. Is only available
                            for Bazel >= 6.0.0 and if flag '--experimental_cc_interface_deps' is provided. Cannot be
                            combbined with use_implementation_deps.
    Returns:
        Configured DWYU aspect
    """
    if use_implementation_deps and use_interface_deps:
        fail("Cannot use 'use_implementation_deps' and 'use_interface_deps' at the same time")
    attr_aspects = ["deps"] if recursive else []
    return aspect(
        implementation = dwyu_aspect_impl,
        attr_aspects = attr_aspects,
        attrs = {
            "_dwyu_binary": attr.label(
                default = Label("@depend_on_what_you_use//src/analyze_includes:analyze_includes"),
                allow_files = True,
                executable = True,
                cfg = "exec",
                doc = "Tool Analyzing the include statement in the source code under inspection" +
                      " and comparing them to the available dependencies.",
            ),
            "_config": attr.label(
                default = config,
                allow_single_file = [".json"],
            ),
            "_recursive": attr.bool(
                default = recursive,
            ),
            "_use_implementation_deps": attr.bool(
                default = use_implementation_deps,
            ),
            "_use_interface_deps": attr.bool(
                default = use_interface_deps,
            ),
        },
    )
