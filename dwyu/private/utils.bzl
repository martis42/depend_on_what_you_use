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
