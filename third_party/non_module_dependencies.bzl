load("//third_party/boost/wave:repository.bzl", "boost_wave")

def _non_module_dependencies_impl(_ctx):
    boost_wave()

non_module_dependencies = module_extension(
    implementation = _non_module_dependencies_impl,
)
