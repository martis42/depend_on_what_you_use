// relative includes to headers from dependencies
#include "some/sub/dir/../dir/bar.h"
#include "some/sub/dir/foo.h"
#include "system_include.h"
// include from virtually prefixed path
#include <sub/../sub/dir/bar.h>

int main() {
    return useSystemInclude() + doBar() + doFoo();
}
