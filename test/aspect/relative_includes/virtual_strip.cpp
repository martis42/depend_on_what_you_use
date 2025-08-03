// relatively including header from own target
#include "some/virtual_strip.h"
#include "other/other.h"
#include "some/sub/dir/bar.h"
// include from virtually stripped path
#include "sub/dir/foo.h"

int useVirtualStrip() {
    return doFoo() + doBar() + doOther();
}
