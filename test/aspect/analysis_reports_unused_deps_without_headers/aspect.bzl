load("@depend_on_what_you_use//dwyu/cc:defs.bzl", "dwyu_cc_aspect_factory")

_DEPS_WITHOUT_HEADERS = [
    Label("//analysis_reports_unused_deps_without_headers:aggregate"),
    Label("//analysis_reports_unused_deps_without_headers:private_only"),
]

report = dwyu_cc_aspect_factory(
    analysis_reports_unused_deps_without_headers = _DEPS_WITHOUT_HEADERS,
)

report_with_private_headers = dwyu_cc_aspect_factory(
    analysis_ignores_private_headers_from_deps = False,
    analysis_reports_unused_deps_without_headers = _DEPS_WITHOUT_HEADERS,
)

report_and_ignore = dwyu_cc_aspect_factory(
    analysis_reports_unused_deps_without_headers = [Label("//analysis_reports_unused_deps_without_headers:aggregate")],
    ignored_unused_deps = [Label("//analysis_reports_unused_deps_without_headers:aggregate")],
)
