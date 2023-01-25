// relatively including header from own target
#include "some/virtual_strip.h"
#include "some/sub/dir/bar.h"
// include from virtually stripped path
#include "sub/dir/foo.h"

int main() {
    return useVirtualStrip() + doBar();
}
