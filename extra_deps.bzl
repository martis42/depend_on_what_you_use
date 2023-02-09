load("@rules_python//python/pip_install:repositories.bzl", _pip_install_dependencies = "pip_install_dependencies")
load("//:requirements.bzl", _install_dwyu_py_deps = "install_deps")

def dwyu_extra_deps(with_workaround = True):
    # FIXME(storypku):
    # Remove workaround below once [rules_python issue #497](https://github.com/bazelbuild/rules_python/issues/497)
    # was resolved.
    if with_workaround:
        _pip_install_dependencies()

    _install_dwyu_py_deps()
