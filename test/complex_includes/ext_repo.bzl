def load_complex_includes_repo():
    native.local_repository(
        name = "complex_includes_repo",
        path = "test/complex_includes/ext_repo",
    )
