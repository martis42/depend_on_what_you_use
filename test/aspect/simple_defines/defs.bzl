def if_foo(if_true, if_false = []):
    return select({
        ":foo_enabled": if_true,
        "//conditions:default": if_false,
    })
