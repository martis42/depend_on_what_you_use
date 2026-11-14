"""
Example of a source-modifying aspect applying the fixes reported by a DWYU aspect.

The aspect requires a DWYU aspect and runs one fix action per target. The action reads the DWYU report of the target
and edits the BUILD file of the target with buildozer. For brevity, the example ignores `implementation_deps`.
"""

load("@rules_cc//cc/common:cc_info.bzl", "CcInfo")

_HeaderOwnerInfo = provider(
    doc = "Headers in the dependency closure of a target and the target owning each header.",
    fields = {
        "header_owners": "depset of (header path, owner label) tuples",
    },
)

def _owner_label(label):
    """
    Label as written in a BUILD file of the main repository.

    `str(label)` yields `@@//pkg:name` for targets of the main repository.
    """
    if label.repo_name:
        return str(label)
    return "//{}:{}".format(label.package, label.name)

def _header_owner_line(header_owner):
    return "{} {}".format(header_owner[0], header_owner[1])

def _find_source_file(ctx):
    """
    The fix tool resolves the workspace root through the symlink of a source file in the execution root.
    """
    files = getattr(ctx.rule.files, "srcs", []) + getattr(ctx.rule.files, "hdrs", [])
    for file in files:
        if file.is_source:
            return file
    return None

def _fix_target(ctx, target, header_owners):
    reports = getattr(target[OutputGroupInfo], "dwyu_report", None)
    source_file = _find_source_file(ctx)
    if target.label.repo_name or not reports or not source_file:
        return []

    header_owners_file = ctx.actions.declare_file("{}_dwyu_fix_header_owners.txt".format(target.label.name))
    header_owners_args = ctx.actions.args()
    header_owners_args.set_param_file_format("multiline")
    header_owners_args.add_all(header_owners, map_each = _header_owner_line)
    ctx.actions.write(header_owners_file, header_owners_args)

    stamp_file = ctx.actions.declare_file("{}_dwyu_fix.stamp".format(target.label.name))
    report_file = reports.to_list()[0]

    args = ctx.actions.args()
    args.add("--report", report_file)
    args.add("--header_owners", header_owners_file)
    args.add("--source_file", source_file)
    args.add("--buildozer", ctx.executable._buildozer)
    args.add("--output", stamp_file)

    ctx.actions.run(
        executable = ctx.executable._fix_deps,
        tools = [ctx.executable._buildozer],
        inputs = [report_file, header_owners_file, source_file],
        outputs = [stamp_file],
        arguments = [args],
        mnemonic = "DwyuFix",
        progress_message = "Fixing dependencies of %{label}",
        # The action edits BUILD files in the source tree. Running it locally disables the sandbox.
        execution_requirements = {"local": "1"},
    )
    return [stamp_file]

def _dwyu_fix_aspect_impl(target, ctx):
    deps = [dep for dep in getattr(ctx.rule.attr, "deps", []) if _HeaderOwnerInfo in dep]
    dep_header_owners = depset(transitive = [dep[_HeaderOwnerInfo].header_owners for dep in deps])

    compilation_context = target[CcInfo].compilation_context
    owner = _owner_label(target.label)
    header_owners = depset(
        direct = [
            (header.path, owner)
            for header in compilation_context.direct_headers + compilation_context.direct_textual_headers
        ],
        transitive = [dep_header_owners],
    )

    stamps = _fix_target(ctx, target = target, header_owners = dep_header_owners)
    dep_stamps = [dep[OutputGroupInfo].dwyu_fix for dep in deps if hasattr(dep[OutputGroupInfo], "dwyu_fix")]

    return [
        _HeaderOwnerInfo(header_owners = header_owners),
        OutputGroupInfo(dwyu_fix = depset(direct = stamps, transitive = dep_stamps)),
    ]

def dwyu_fix_aspect_factory(dwyu_aspect):
    """
    Create an aspect fixing the findings of a DWYU aspect.

    Args:
        dwyu_aspect: DWYU aspect created with `dwyu_cc_aspect_factory`. The DWYU aspect runs on every target the fix
                     aspect visits.

    Returns:
        Configured fix aspect
    """
    return aspect(
        implementation = _dwyu_fix_aspect_impl,
        attr_aspects = ["deps"],
        required_providers = [CcInfo],
        requires = [dwyu_aspect],
        attrs = {
            "_buildozer": attr.label(
                default = Label("@buildozer_binary//:buildozer.exe"),
                allow_single_file = True,
                executable = True,
                cfg = "exec",
            ),
            "_fix_deps": attr.label(
                default = Label("//dwyu_fix:fix_deps"),
                executable = True,
                cfg = "exec",
            ),
        },
    )
