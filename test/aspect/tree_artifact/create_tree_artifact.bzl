def _create_tree_artifact_impl(ctx):
    if not ctx.attr.tree_root.endswith((".h", ".cc")):
        fail("Target directory must end with a file ending recognized as C++ rule iput")

    tree_artifact = ctx.actions.declare_directory(ctx.attr.tree_root)

    args = ctx.actions.args()
    args.add("--tree_root", tree_artifact.path)
    args.add("--tree_part", ctx.attr.tree_part)
    if ctx.attr.verbose:
        args.add("--verbose")

    ctx.actions.run(
        arguments = [args],
        executable = ctx.executable._creator,
        outputs = [tree_artifact],
    )

    return DefaultInfo(files = depset([tree_artifact]))

_create_tree_artifact = rule(
    implementation = _create_tree_artifact_impl,
    attrs = {
        "tree_part": attr.string(),
        "tree_root": attr.string(),
        "verbose": attr.bool(default = False),
        "_creator": attr.label(executable = True, cfg = "exec", default = "//tree_artifact:create_tree"),
    },
)

# buildifier: disable=unnamed-macro
def create_tree_artifacts(public_headers, private_headers, sources, verbose = False):
    _create_tree_artifact(
        name = public_headers,
        tree_root = public_headers,
        tree_part = "public_headers",
        verbose = verbose,
    )

    _create_tree_artifact(
        name = private_headers,
        tree_root = private_headers,
        tree_part = "private_headers",
        verbose = verbose,
    )

    _create_tree_artifact(
        name = sources,
        tree_root = sources,
        tree_part = "sources",
        verbose = verbose,
    )
