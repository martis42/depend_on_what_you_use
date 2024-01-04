// relative includes to headers from dependencies
#include "virtual_prefix.h"
#include "some/sub/dir/bar.h"
#include "some/sub/dir/../dir/bar.h"
// reach into virtual paths from repository root
#include "relative_includes/_virtual_includes/virtual_prefix/custom/prefix/some/sub/dir/foo.h"
// include from virtually prefixed path
#include "../virtual_prefix/custom/prefix/some/sub/dir/foo.h"
#include "custom/prefix/../prefix/some/sub/dir/foo.h"

int main() {
    return useVirtualPrefix() + doBar() + doFoo();
}
