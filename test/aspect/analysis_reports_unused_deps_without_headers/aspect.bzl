load("@depend_on_what_you_use//dwyu/cc:defs.bzl", "dwyu_cc_aspect_factory")

report = dwyu_cc_aspect_factory(
    analysis_reports_unused_deps_without_headers = [Label("//analysis_reports_unused_deps_without_headers:aggregate")],
)

report_and_ignore = dwyu_cc_aspect_factory(
    analysis_reports_unused_deps_without_headers = [Label("//analysis_reports_unused_deps_without_headers:aggregate")],
    ignored_unused_deps = [Label("//analysis_reports_unused_deps_without_headers:aggregate")],
)
