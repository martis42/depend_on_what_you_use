// relatively including header from own target
#include "virtual_prefix.h"
#include "other/other.h"
#include "some/sub/dir/bar.h"
// include from virtually prefixed path
#include "custom/prefix/some/sub/dir/foo.h"

int useVirtualPrefix() {
    return doFoo() + doBar() + doOther();
}
