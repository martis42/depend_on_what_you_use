# buildifier: disable=unnamed-macro
def load_external_targets():
    native.local_repository(
        name = "external_targets",
        path = "support/external_targets",
    )
