visibility("//dwyu/...")

def label_to_name(label):
    """
    Create a legal name from a string describing a Bazel target label
    """
    return str(label).replace("@", "").replace("//", "_").replace("/", "_").replace(":", "_")

def make_param_file_args(ctx):
    args = ctx.actions.args()

    args.set_param_file_format("multiline")
    args.use_param_file("--param_file=%s")

    return args

def string_to_bool(value):
    if value.lower() in ["true", "1", "yes"]:
        return True
    elif value.lower() in ["false", "0", "no"]:
        return False
    else:
        fail("Invalid boolean value: {}".format(value))

def unique_list(list_a, list_b):
    """
    Combine two lists and return a new list without duplicates, preserving order of first occurrence.
    """
    return {x: None for x in list_a + list_b}.keys()
