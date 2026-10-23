# Applying automatic fixes

> [!WARNING]
> Please note that **the tool cannot guarantee that your build is not being broken** by the changes.
> Always make sure your project is still valid after the changes and review the performed changes.

> [!NOTE]
> This tool is executing Bazel commands.
> If one needs to configure bazel commands with custom options in your workspace, please have a look at the `--bazel-args` and `--bazel-startup-args` options of this tool.

The general workflow is the following:

1. Execute DWYU on your workspace.
   DWYU will create report files containing information about discovered problems in the Bazel output directory.
1. Execute `bazel run @depend_on_what_you_use//dwyu/apply_fixes:apply_fixes -- <your_options>`.
   The tool discovers the report files generated in the previous step and gathers the problems for which a fix is available.
   Then, [buildozer](https://github.com/bazelbuild/buildtools/blob/master/buildozer/README.md) is utilized to adapt the BUILD files in your workspace.

We recommend:

- Execute the DWYU analysis build with `--keep_going` to generate the DWYU reports to find all issues at once.
- Pipe the terminal output from executing DWYU into a file.
  Then, provide this log file to `@depend_on_what_you_use//dwyu/apply_fixes:apply_fixes` via the `--dwyu-log-file` option.
  This is the fastest and most robust option to make the DWYU reports available to the `apply_fixes` tool.

The `apply_fixes` tool requires you to explicitly choose which kind or errors you want to be fixed.
You can see the full command line interface and more information about the script behavior and limitations by executing:<br>
`bazel run @depend_on_what_you_use//dwyu/apply_fixes:apply_fixes -- --help`

If you are not using `--dwyu-log-file`, the `apply_fixes` tool searches by itself for the DWYU reports in the output base, which can be slow for large workspaces.

Unfortunately, the tool cannot promise perfect results due to various constraints:

- If alias targets are involved, this cannot be processed properly.
  Alias targets are resolved to their actual target before the DWYU aspect is running.
  Thus, the DWYU report file contains the actual targets in its report and buildozer is not able to modify the BUILD files containing the alias name.
- Buildozer is working on the plain BUILD files as a user would see them in the editor.
  Meaning without alias resolution or macro expansion.
  Consequently, buildozer cannot work on targets which are generated inside a macro or whose name is constructed.
- Adding missing direct dependencies is based on a heuristic and not guaranteed to find the correct dependency.
