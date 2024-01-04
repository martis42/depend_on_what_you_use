# buildifier: disable=unnamed-macro
def load_external_repo():
    native.local_repository(
        name = "external_test_repo",
        path = "external_repo/repo",
    )
