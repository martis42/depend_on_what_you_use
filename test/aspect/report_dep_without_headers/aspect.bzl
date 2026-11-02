load("@depend_on_what_you_use//dwyu/cc:defs.bzl", "dwyu_cc_aspect_factory")

report = dwyu_cc_aspect_factory(
    report_dep_without_headers = [Label("//report_dep_without_headers:aggregate")],
)

report_and_ignore = dwyu_cc_aspect_factory(
    report_dep_without_headers = [Label("//report_dep_without_headers:aggegate")],
    ignored_unused_deps = [Label("//report_dep_without_headers:aggregate")],
)
