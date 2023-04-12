# buildifier: disable=unnamed-macro
def load_external_dep():
    native.local_repository(
        name = "external_dep",
        path = "external_dep",
    )
