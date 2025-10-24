load("//third_party/boost/wave:repository.bzl", "boost_wave")
load("//third_party/pcpp:repository.bzl", "pcpp")
load("//third_party/rules_boost:rules_boost_step_1.bzl", "rules_boost_step_1")

def _non_module_dependencies_step_1_impl(_ctx):
    pcpp()
    rules_boost_step_1()
    boost_wave()

non_module_dependencies_step_1 = module_extension(
    implementation = _non_module_dependencies_step_1_impl,
)
