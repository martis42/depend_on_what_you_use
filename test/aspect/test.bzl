load("//test/aspect/complex_includes:ext_repo.bzl", "load_complex_includes_repo")
load("//test/aspect/external_repo:repo.bzl", "load_external_repo")

# buildifier: disable=unnamed-macro
def test_setup():
    load_external_repo()
    load_complex_includes_repo()
