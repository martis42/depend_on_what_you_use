import logging
import sys
from argparse import REMAINDER, ArgumentParser, Namespace, RawDescriptionHelpFormatter

from src.apply_fixes.apply_fixes import main

logging.basicConfig(format="%(message)s", level=logging.INFO)


def cli() -> Namespace:
    parser = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        description="""
This script expects that the user has invoked DWYU in the given workspace beforehand and by doing so generated DYWU
report files in the output path.
Running this script multiple times on the same report files will not break anything, but will cause a lot of warnings,
since all issues are already fixed. Always execute the DWYU aspect to generate fresh report files before executing
this script.

Beware that there are limits on what buildozer can achieve. Buildozer works on a limited set of information, since
it looks at BUILD files before macro and alias expansion:
- If targets are generated by macros buildozer cannot edit them.
- The DWYU aspect runs after alias expansion and thus reports the actual names instead of the alias names. However,
  only the alias name is visible to buildozer in a BUILD file in the dependencies of a target.

The script expects 'bazel' to be available on PATH.
    """.strip(),
    )
    parser.add_argument(
        "--workspace",
        metavar="PATH",
        help="""
        Workspace for which DWYU reports are gathered and fixes are applied to the source code. If no dedicated
        workspace is provided, we assume we are running from within the workspace for which the DWYU reports have been
        generated and determine the workspace root automatically.
        By default the Bazel output directory containing the DWYU report files is deduced by following the 'bazel-bin'
        convenience symlink.""",
    )
    parser.add_argument(
        "--use-bazel-info",
        const="fastbuild",
        choices=["dbg", "fastbuild", "opt"],
        nargs="?",
        help="""
        Don't follow the convenience symlinks to reach the Bazel output directory containing the DWYU reports. Instead,
        use 'bazel info' to deduce the output directory.
        This option accepts an optional argument specifying the compilation mode which was used to generate the DWYU
        report files.
        Using this option is recommended if the convenience symlinks do not exist, don't follow the default
        naming scheme or do not point to the Bazel output directory containing the DWYU reports.""",
    )
    parser.add_argument(
        "--search-path",
        metavar="PATH",
        help="""
        Path to the directory below which the DWYU reports are located.
        Using this option is recommended if neither the convenience symlinks nor the 'bazel info' command are suited to
        deduce the Bazel output directory containing the DWYU report files. Or if you want to search only in a sub tree
        of the Bazel output directories.""",
    )
    parser.add_argument(
        "--use-cquery",
        action="store_true",
        help="""
        The apply_fixes script by default uses 'bazel query' to find missing dependencies. Your project might use
        select statements to exchange dependencies. In such cases you should use 'bazel cquery' to allow this script
        understanding the dependency tree properly. Should be used together with '--bazel-args' to provide
        the configuration for 'bazel cquery'.""",
    )
    parser.add_argument(
        "--bazel-args",
        type=str,
        metavar="STRING",
        help="""
        The apply_fixes script uses 'bazel (c)query' to find missing dependencies. If this command requires further
        arguments to work properly in your workspace you can provide them here. Also look into '--use-cquery' if
        you want to provide build configuration.
        Arguments have ot be provided as one large string, e.g.: --bazel-args='--foo --tick=tock'.""",
    )
    parser.add_argument(
        "--bazel-startup-args",
        type=str,
        metavar="STRING",
        help="""
        The apply_fixes script uses 'bazel (c)query' to find missing dependencies. If this command requires further
        startup arguments (e.g. a custom output base) to work properly in your workspace you can provide them here.
        Arguments have ot be provided as one large string, e.g.: --bazel-args='--foo --tick=tock'.""",
    )
    parser.add_argument(
        "--fix-unused-deps",
        action="store_true",
        help="Automatically remove unused dependencies.",
    )
    parser.add_argument(
        "--fix-deps-which-should-be-private",
        action="store_true",
        help="Automatically move 'deps' to 'implementation_deps'.",
    )
    parser.add_argument(
        "--fix-missing-deps",
        action="store_true",
        help="""
        Automatically search and add dependencies providing headers for which a direct dependency is missing. This is
        based on a heuristic and thus is not guaranteed to work.""",
    )
    parser.add_argument(
        "--fix-all",
        action="store_true",
        help="Perform all available automatic fixes.",
    )
    parser.add_argument(
        "--buildozer",
        metavar="PATH",
        help="""
        buildozer binary which shall be used by this script. If none is provided, it is expected to find buildozer on
        PATH.""",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't apply fixes. Report the buildozer commands and print the adapted BUILD files to stdout.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Announce intermediate steps.",
    )
    parser.add_argument(
        "--buildozer-args",
        nargs=REMAINDER,
        help="Forward arguments to buildozer. Has to be the last option in the command line.",
    )

    args = parser.parse_args()

    has_explicit_fix_option = any((args.fix_unused_deps, args.fix_deps_which_should_be_private, args.fix_missing_deps))
    if not has_explicit_fix_option and not args.fix_all:
        logging.fatal("Please choose at least one of the 'fix-..' options")
        sys.exit(1)

    return args


if __name__ == "__main__":
    cli_args = cli()
    sys.exit(main(cli_args))
