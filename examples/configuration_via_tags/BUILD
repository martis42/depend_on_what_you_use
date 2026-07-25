load("@rules_cc//cc:cc_library.bzl", "cc_library")
load(":to_canonical.bzl", "to_canonical")

# Those are some examples for using tags to control the DWYU behavior.
# Not all options are demonstrated, but just a select few.
# For a complete list of tags see the aspect documentation.

# Specifies an unused dependency, which would fail the DWYU analysis
cc_library(
    name = "skipped_target",
    hdrs = ["lib_1.h"],
    tags = ["dwyu:skip"],
    deps = [":foo"],
)

# We use DWYU on this target, but tell DWYU to ignore a specific unused dependency
cc_library(
    name = "exception_for_unused_deps",
    hdrs = ["lib_1.h"],
    tags = ["dwyu:ignore_unused_dep={}".format(to_canonical(":foo"))],
    deps = [":foo"],
)

# If the problem with the unused dependency check is not with specific targets, but a general one, we can disable the whole check
cc_library(
    name = "disable_check_for_unused_deps",
    hdrs = ["lib_1.h"],
    tags = ["dwyu:report_unused_deps=False"],
    deps = [":foo"],
)

# Using a header from a transitive dependency would fail, unless we tell DWYU to ignore the inclusion of that header
cc_library(
    name = "exception_for_include_of_transitive_dependency",
    hdrs = ["lib_2.h"],
    tags = ["dwyu:ignore_include=configuration_via_tags/bar.h"],
    deps = [":foo"],
)

#
# Support targets
#

cc_library(
    name = "foo",
    hdrs = ["foo.h"],
    deps = [":bar"],
)

cc_library(
    name = "bar",
    hdrs = ["bar.h"],
)
