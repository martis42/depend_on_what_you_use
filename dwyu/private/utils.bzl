visibility("//dwyu/...")

def label_to_name(label):
    """
    Create a legal name from a string describing a Bazel target label
    """
    return str(label).replace("@", "").replace("//", "_").replace("/", "_").replace(":", "_")
