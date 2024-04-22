cc_library(
    name = "broken_dep",
    hdrs = ["broken_dep.h"],
    deps = [":a"],  # Missing dependency to //lib:b
)

cc_library(
    name = "a",
    hdrs = ["lib/a.h"],
    deps = [":b"],
)

cc_library(
    name = "b",
    hdrs = ["lib/b.h"],
)
