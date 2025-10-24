load("//third_party/rules_boost:rules_boost_step_2.bzl", "rules_boost_step_2")

def _non_module_dependencies_step_2_impl(_ctx):
    rules_boost_step_2()

non_module_dependencies_step_2 = module_extension(
    implementation = _non_module_dependencies_step_2_impl,
)
