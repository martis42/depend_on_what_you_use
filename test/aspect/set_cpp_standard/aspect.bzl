load("@depend_on_what_you_use//:defs.bzl", "dwyu_aspect_factory")

set_cplusplus = dwyu_aspect_factory(experimental_set_cplusplus = True)

set_cplusplus_cpp = dwyu_aspect_factory(experimental_set_cplusplus = True, use_cpp_implementation = True)
