from __future__ import annotations

import shutil
from pathlib import Path

from test.support.platform import path_to_starlark_format

ASPECT_TEMPLATE = "test/cc_toolchains/upstream/aspect.bzl.tpl"
ASPECT_TEMPLATE_CPP = "test/cc_toolchains/upstream/aspect_cpp.bzl.tpl"
BAZELRC_TEMPLATE = "test/cc_toolchains/upstream/bazelrc.tpl"
BUILD_TEMPLATE = "test/cc_toolchains/upstream/BUILD.tpl"
HEADER_TEMPLATE = "test/cc_toolchains/upstream/use_toolchain_headers.h.tpl"

MODULE_TEMPLATE = """
module(name = "dwyu_upstream_cc_toolchain_integration_tests")

bazel_dep(name = "depend_on_what_you_use")
local_path_override(module_name = "depend_on_what_you_use", path = "{dwyu_path}")

# We specify by design an outdated rules_cc version.
# bzlmod resolves dependencies to the maximum of all requested versions for all involved modules.
# Specifying an ancient version here gives us in the end whatever the other involved modules need.
bazel_dep(name = "rules_cc", version = "0.0.1")

{extra_content}
"""


def prepare_workspace(workspace: Path, dwyu_path: Path, module_extra_content: str, use_cpp_impl: bool) -> None:
    workspace.mkdir(parents=True, exist_ok=True)

    aspect_template = ASPECT_TEMPLATE_CPP if use_cpp_impl else ASPECT_TEMPLATE
    shutil.copy(dwyu_path / aspect_template, workspace / "aspect.bzl")
    shutil.copy(dwyu_path / BAZELRC_TEMPLATE, workspace / ".bazelrc")
    shutil.copy(dwyu_path / BUILD_TEMPLATE, workspace / "BUILD")
    shutil.copy(dwyu_path / HEADER_TEMPLATE, workspace / "use_toolchain_headers.h")

    module_file = workspace / "MODULE.bazel"
    module_file.write_text(
        MODULE_TEMPLATE.format(dwyu_path=path_to_starlark_format(dwyu_path), extra_content=module_extra_content)
    )
