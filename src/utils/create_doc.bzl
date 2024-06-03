load("@aspect_bazel_lib//lib:write_source_files.bzl", "write_source_file")
load("@stardoc//stardoc:stardoc.bzl", "stardoc")

def create_doc(name, input, out, deps, **kwargs):
    """
    Create documentation with stardoc and offer consistency enforcement with little boilerplate.

    Args:
        name: Unique name
        input: .bzl for which documentation shall be generated
        out: Label of target documentation file in workspace
        deps: bzl_library targets required to parse the input
        **kwargs: Common rule arguments like visibility or tags
    """
    doc_file = "{}_doc.md".format(input)

    stardoc(
        name = name,
        out = doc_file,
        input = input,
        deps = deps,
        **kwargs
    )

    write_source_file(
        name = "{}_write_src".format(name),
        in_file = doc_file,
        out_file = out,
        check_that_out_file_exists = False,
        **kwargs
    )
