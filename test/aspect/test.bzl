load("//test/aspect/external_repo:repo.bzl", "load_external_repo")
load("//test/aspect/complex_includes:ext_repo.bzl", "load_complex_includes_repo")

def test_setup():
    load_external_repo()
    load_complex_includes_repo()
