load("//third_party/pcpp:repository.bzl", "pcpp")

def _non_module_dependencies_impl(_ctx):
    pcpp()

non_module_dependencies = module_extension(
    implementation = _non_module_dependencies_impl,
)
