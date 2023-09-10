// relative includes to headers from dependencies
#include "system_include.h"
#include "some/sub/dir/foo.h"
#include "some/sub/dir/../dir/bar.h"
// include from virtually prefixed path
#include <sub/../sub/dir/bar.h>
#include <../some/sub/dir/bar.h>

int main() {
    return useSystemInclude() + doBar() + doFoo();
}
