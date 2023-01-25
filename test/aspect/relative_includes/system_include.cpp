// relatively including header from own target
#include "system_include.h"
#include "some/sub/dir/bar.h"
// include from virtually prefixed path
#include <sub/dir/foo.h>

int useSystemInclude() {
    return doFoo() + doBar();
}
