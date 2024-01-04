// relatively including header from own target
#include "normal_include.h"
#include "some/sub/dir/foo.h"
// normal include relative to workspace root
#include "relative_includes/some/sub/dir/bar.h"

int useNormalInclude() {
    return doFoo() + doBar();
}
