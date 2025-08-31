load("//third_party:rules_boost.bzl", "rules_boost")
load("//third_party/pcpp:repository.bzl", "pcpp")

def _non_module_dependencies_step_1_impl(_ctx):
    pcpp()
    rules_boost()

non_module_dependencies_step_1 = module_extension(
    implementation = _non_module_dependencies_step_1_impl,
)
