def load_external_repo():
    native.local_repository(
        name = "ext_repo",
        path = "test/aspect/external_repo/repo",
    )
