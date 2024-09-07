# buildifier: disable=unnamed-macro
def make_large_defines(minimum_characters):
    fake_define = "_0123456789_ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz"
    steps = int(minimum_characters / len(fake_define)) + 1
    return ["{i}{define}".format(i = i, define = fake_define) for i in range(steps)]
