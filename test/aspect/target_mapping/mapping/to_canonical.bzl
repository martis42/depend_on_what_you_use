def to_canonical(target):
    """
    We can't use the 'Label()' constructor in BUILD files without the indirection through a macro.
    """
    return str(Label(target))
