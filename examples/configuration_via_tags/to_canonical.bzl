def to_canonical(apparent_name):
    """
    Convert a target using the apparent repo name to one using the canonical repo name.
    This has to be a macro, since the 'Label' function is not available in BUILD files.

    Please note, this macro has to live in the client workspace.
    Reusing it from another workspace will not work, as then the 'Label' function will resolve relative to the workspace from which you load the macro.
    """
    return str(Label(apparent_name))
