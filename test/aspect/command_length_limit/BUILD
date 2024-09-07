"""
Show that the DWYU aspect can handle cases where some attributes of the target under inspection are so large that the
resulting command invocations are larger than the system's command length limits.

We only test the command line length limit for the target processing step. A test for the analysis step would have an
enormous runtime. Such a scenario is unlikely in a real project and thus we skip it for now.
"""

load(":make_large_arg.bzl", "make_large_defines")

CHARACTERS_IN_COMMAND = 5000000

cc_library(
    name = "many_defines",
    hdrs = ["foo.h"],
    local_defines = make_large_defines(CHARACTERS_IN_COMMAND),
)
