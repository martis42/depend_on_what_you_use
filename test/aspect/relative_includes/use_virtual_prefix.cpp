// relatively including header from own target
#include "virtual_prefix.h"
#include "some/sub/dir/bar.h"
#include "some/sub/dir/../dir2/baz.h"
// include from virtually prefixed path
#include "custom/prefix/some/sub/dir/foo.h"

int main() {
    return useVirtualPrefix() + doBar() + doBaz();
}
