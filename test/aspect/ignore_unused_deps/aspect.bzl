load("@depend_on_what_you_use//dwyu/cc:defs.bzl", "dwyu_cc_aspect_factory")

dwyu_ignore_unused_deps = dwyu_cc_aspect_factory(ignored_unused_deps = [Label("//ignore_unused_deps:foo"), Label("@ignore_unused_deps_test_repo//:ext")])
