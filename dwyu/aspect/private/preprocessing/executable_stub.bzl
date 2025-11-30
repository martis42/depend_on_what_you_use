def _executable_stub_impl(ctx):
    ctx.actions.write(output = ctx.outputs.executable, is_executable = True, content = "Irrelevant, will never be called")
    return [DefaultInfo(
        files = depset([ctx.outputs.executable]),
        executable = ctx.outputs.executable,
    )]

executable_stub = rule(
    implementation = _executable_stub_impl,
    executable = True,
)
