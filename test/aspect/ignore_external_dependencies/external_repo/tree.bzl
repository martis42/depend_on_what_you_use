def _external_header_tree_impl(ctx):
    tree = ctx.actions.declare_directory(ctx.label.name)
    ctx.actions.run_shell(
        outputs = [tree],
        arguments = [tree.path],
        command = "mkdir -p \"$1\" && printf '%s\\n' '#ifndef GENERATED_TREE_H_HEADER_H' '#define GENERATED_TREE_H_HEADER_H' 'int treeExternal();' '#endif' > \"$1/header.h\"",
    )
    return [DefaultInfo(files = depset([tree]))]

external_header_tree = rule(implementation = _external_header_tree_impl)
