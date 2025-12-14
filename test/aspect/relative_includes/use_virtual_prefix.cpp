// relative includes to headers from dependencies
#include "some/sub/dir/../dir/bar.h"
#include "some/sub/dir/bar.h"
#include "virtual_prefix.h"
// include from virtually prefixed path
#include "custom/prefix/../prefix/some/sub/dir/foo.h"

int main() {
    return useVirtualPrefix() + doBar() + doFoo();
}
