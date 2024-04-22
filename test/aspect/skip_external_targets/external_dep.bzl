# buildifier: disable=unnamed-macro
def load_external_dep():
    native.local_repository(
        name = "skip_external_deps_test_repo",
        path = "skip_external_targets/external_dep",
    )
