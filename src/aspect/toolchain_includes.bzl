load("@bazel_tools//tools/cpp:toolchain_utils.bzl", "find_cpp_toolchain")

##
load("//src/utils:utils.bzl", "print_cc_toolchain")

def _toolchain_includes_impl(ctx):
    cc_toolchain = find_cpp_toolchain(ctx)
    print_cc_toolchain(cc_toolchain)

    bar = ctx.actions.declare_file("{name}.json".format(ctx.name))
    args = ctx.actions.args()
    args.add_all("--include_directories", cc_toolchain.built_in_include_directories, omit_if_empty = False)
    args.add_all("--toolchain_files", cc_toolchain.all_files, omit_if_empty = False)
    args.add("--output", bar)    
    ctx.actions.run(
        executable = ctx.executable._parser,
        inputs = cc_toolchain.all_files,
        outputs = [bar],
        #mnemonic = "DWYU_TBD",
        #progress_message = "DWYU TBD",
        arguments = [args],
    )

    #foo = depset(direct = [bar])
    return [DefaultInfo(files = depset(direct = [bar]))]

toolchain_includes = rule(
    implementation = _toolchain_includes_impl,
    toolchains = ["@bazel_tools//tools/cpp:toolchain_type"],
    attrs = {
        "_cc_toolchain": attr.label(
            default = Label("@bazel_tools//tools/cpp:current_cc_toolchain"),

        ),    
        "_parser": attr.label(
            default = Label("@depend_on_what_you_use//src/aspect:toolchain_includes"),
            executable = True,
            cfg = "exec",
            doc = "TBD",
        ),
    }
)