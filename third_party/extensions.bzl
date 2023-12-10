load("//third_party:dev_dependencies.bzl", "dev_dependencies")

def _non_module_dependencies_impl(_ctx):
    dev_dependencies()

non_module_dependencies = module_extension(
    implementation = _non_module_dependencies_impl,
)
