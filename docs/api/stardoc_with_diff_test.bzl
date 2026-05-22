"""
Helpers for generating stardoc documentation

Inspired by https://github.com/bazel-contrib/bazel-lib/blob/2befef614904d0ebe5161beb271ac31c83e82fd2/lib/private/docs.bzl

We cannot depend on the upstream version, as they deleted this for version 3.x and the contribution to stardoc which
was discussed in https://github.com/bazel-contrib/bazel-lib/issues/1185 did not yet happen at the time of creating
this. We adapted to upstream version to simplify it for us.
"""

load("@bazel_lib//lib:write_source_files.bzl", "write_source_files")
load("@stardoc//stardoc:stardoc.bzl", _stardoc = "stardoc")

visibility("private")

def stardoc(name, bzl_target, out_file, **kwargs):
    """
    Convenience wrapper around _stardoc() for generating stardoc targets in a way the update_and_test_docs() rule can
    automatically pick up the stardoc() targets.

    Args:
        name: Unique name for the stardoc target
        bzl_target: The `bzl_library` target to generate documentation for. We expect the target name ending with
                    '_bzl' and the target containing a source file named accordingly.
        out_file: The MD file which shall be generated for 'bzl_library_target'
        **kwargs: Additional attributes passed to the _stardoc() rule
    """

    if not bzl_target.endswith("_bzl"):
        fail("bzl_target '{}' does not follow the expected naming scheme".format(bzl_target))

    _stardoc(
        name = name + ".stardoc",
        out = out_file.replace(".md", ".docgen.md"),
        input = bzl_target.replace("_bzl", ".bzl"),
        deps = [bzl_target],
        **kwargs
    )

def update_and_test_docs(name = "update", **kwargs):
    """
    Creates a diff_test for checking the consistency of stardoc() targets in the same package and
    provides a target for updating those.

    Args:
        name: Name of the file updating target
        **kwargs: Additional attributes passed to the write_source_files() rule
    """

    update_files = {}
    for r in native.existing_rules().values():
        if r["name"].endswith(".stardoc"):
            generated_file_name = r["out"]
            source_file_name = generated_file_name.replace(".docgen.md", ".md")
            update_files[source_file_name] = generated_file_name

    write_source_files(
        name = name,
        files = update_files,
        **kwargs
    )
