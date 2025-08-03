#!/usr/bin/env python3
import logging
import sys
from argparse import ArgumentParser, Namespace
from os import chdir
from pathlib import Path

# Allow importing test support code. Relative imports do not work in our case.
# We do this centrally here, so all code we import while executing this knows the extended PYTHONPATH
# ruff: noqa: E402
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(WORKSPACE_ROOT))

from execution_logic import main
from test_case import CompatibleVersions, TestedVersions

logging.basicConfig(format="%(message)s", level=logging.INFO)
log = logging.getLogger()

# Test matrix. We don't combine each Bazel version with each Python version as there is no significant benefit. We
# manually define pairs which make sure each Bazel and Python version we care about is used at least once.
# For versions using the legacy WORKSPACE setup we have to specify the patch version for Python
TESTED_VERSIONS = [
    TestedVersions(bazel="6.4.0", python="3.8"),
    TestedVersions(bazel="7.0.0", python="3.9"),
    TestedVersions(bazel="7.x", python="3.10"),
    TestedVersions(bazel="8.0.0", python="3.11"),
    TestedVersions(bazel="8.x", python="3.12", is_default=True),
    TestedVersions(bazel="rolling", python="3.13"),
]

VERSION_SPECIFIC_ARGS = {
    "--enable_bzlmod": CompatibleVersions(minimum="6.2.0", before="7.0.0"),
    # Reduce noise in test logs
    "--check_direct_dependencies=off": CompatibleVersions(minimum="6.0.0"),
    # Experimental changes we want to be compatible for
    "--experimental_python_import_all_repositories=false": CompatibleVersions(minimum="1.0.0"),
    # Preparation for incompatible changes
    "--incompatible_legacy_local_fallback=false": CompatibleVersions(minimum="5.0.0"),  # false is the forward path
    "--incompatible_enforce_config_setting_visibility": CompatibleVersions(minimum="5.0.0"),
    "--incompatible_config_setting_private_default_visibility": CompatibleVersions(minimum="5.0.0"),
    "--incompatible_disable_target_provider_fields": CompatibleVersions(minimum="5.0.0"),
    "--incompatible_struct_has_no_methods": CompatibleVersions(minimum="5.0.0", before="8.0.0"),
    "--incompatible_use_platforms_repo_for_constraints": CompatibleVersions(minimum="5.0.0", before="7.0.0"),
    "--incompatible_disallow_empty_glob": CompatibleVersions(minimum="5.0.0"),
    "--incompatible_no_implicit_file_export": CompatibleVersions(minimum="5.0.0"),
    "--incompatible_use_cc_configure_from_rules_cc": CompatibleVersions(minimum="5.0.0"),
    "--incompatible_default_to_explicit_init_py": CompatibleVersions(minimum="5.0.0"),
    "--incompatible_exclusive_test_sandboxed": CompatibleVersions(minimum="5.0.0"),
    "--incompatible_strict_action_env": CompatibleVersions(minimum="5.0.0"),
    "--incompatible_disable_starlark_host_transitions": CompatibleVersions(minimum="6.0.0"),
    "--incompatible_sandbox_hermetic_tmp": CompatibleVersions(minimum="6.0.0", before="9.0.0"),
    "--incompatible_check_testonly_for_output_files": CompatibleVersions(minimum="6.0.0"),
    "--incompatible_auto_exec_groups": CompatibleVersions(minimum="7.0.0"),
    "--incompatible_disable_non_executable_java_binary": CompatibleVersions(minimum="7.0.0"),
    "--incompatible_python_disallow_native_rules": CompatibleVersions(minimum="7.0.0"),
    "--incompatible_disallow_struct_provider_syntax": CompatibleVersions(minimum="7.0.0"),
    "--incompatible_use_plus_in_repo_names": CompatibleVersions(minimum="7.2.0"),
    "--incompatible_disable_native_repo_rules": CompatibleVersions(minimum="7.2.0"),
    # Theoretically of interest for us, but rules_python does not comply to this.
    # "--incompatible_stop_exporting_language_modules": CompatibleVersions(minimum="6.0.0"),
    # "--incompatible_enable_deprecated_label_apis=false": CompatibleVersions(minimum="7.0.0"),  # false is the forward path
}


def cli() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("--verbose", "-v", action="store_true", help="Show output of test runs.")
    parser.add_argument(
        "--bazel",
        "-b",
        metavar="VERSION",
        help="Run tests with the specified Bazel version. Also requires setting '--python'",
    )
    parser.add_argument(
        "--python",
        "-p",
        metavar="VERSION",
        help="Run tests with the specified Python version."
        " Has to be one of the versions for which we register a hermetic toolchain. Also requires setting '--bazel'.",
    )
    parser.add_argument(
        "--only-default-version",
        "-d",
        action="store_true",
        help="Execute tests only for the default Bazel and Python version.",
    )
    parser.add_argument("--list", "-l", action="store_true", help="List all available test cases and return.")
    parser.add_argument(
        "--test",
        "-t",
        nargs="+",
        help="Run the specified test cases. Substrings will match against all test names including them.",
    )
    parser.add_argument(
        "--no_output_base",
        action="store_true",
        help="Do not create a dedicated output base per test. Optimizes CI runs for which dedicated outout bases are a slowdown, as the system is either way thrown away.",
    )

    parsed_args = parser.parse_args()
    if (parsed_args.bazel and not parsed_args.python) or (not parsed_args.bazel and parsed_args.python):
        log.error("ERROR: '--bazel' and '--python' have to be used together")
        sys.exit(1)

    return parsed_args


if __name__ == "__main__":
    args = cli()
    if args.verbose:
        log.setLevel(logging.DEBUG)

    # Ensure we can invoke the script from various places
    chdir(Path(__file__).parent)

    sys.exit(
        main(
            tested_versions=TESTED_VERSIONS,
            version_specific_args=VERSION_SPECIFIC_ARGS,
            bazel=args.bazel,
            python=args.python,
            requested_tests=args.test,
            list_tests=args.list,
            only_default_version=args.only_default_version,
            no_output_base=args.no_output_base,
        )
    )
