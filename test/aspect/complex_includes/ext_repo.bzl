# buildifier: disable=unnamed-macro
def load_complex_includes_repo():
    native.local_repository(
        name = "complex_includes_test_repo",
        path = "complex_includes/ext_repo",
    )
