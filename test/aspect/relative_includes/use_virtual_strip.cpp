// relative includes to headers from dependencies
#include "some/sub/dir/../dir/bar.h"
#include "some/sub/dir/bar.h"
#include "some/virtual_strip.h"
// include from virtually stripped path
#include "sub/dir/../dir/foo.h"

int main() {
    return useVirtualStrip() + doBar() + doFoo();
}
