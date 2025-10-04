# buildifier: disable=unnamed-macro
def make_large_defines(minimum_characters):
    fake_define = "__{n}_ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz__"
    steps = int(minimum_characters / (len(fake_define) - 2)) + 1
    return [fake_define.format(n = i) for i in range(steps)]
