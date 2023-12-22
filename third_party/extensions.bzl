load("//third_party:dev_dependencies.bzl", "dev_dependencies")
load("//third_party/pcpp:repository.bzl", "pcpp")

def _non_module_dev_dependencies_impl(_ctx):
    dev_dependencies()

non_module_dev_dependencies = module_extension(
    implementation = _non_module_dev_dependencies_impl,
)

def _non_module_dependencies_impl(_ctx):
    pcpp()

non_module_dependencies = module_extension(
    implementation = _non_module_dependencies_impl,
)
