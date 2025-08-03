// relative includes to headers from dependencies
#include "some/sub/dir/../dir/bar.h"
#include "some/sub/dir/bar.h"
#include "some/virtual_strip.h"
// reach into virtual paths from repository root
#include "relative_includes/_virtual_includes/virtual_strip/sub/dir/foo.h"
// include from virtually stripped path
#include "../virtual_strip/sub/dir/foo.h"
#include "sub/dir/../dir/foo.h"

int main() {
    return useVirtualStrip() + doBar() + doFoo();
}
