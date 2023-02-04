// relative includes to headers from dependencies
#include "normal_include.h"
#include "some/sub/dir/foo.h"
#include "some/sub/dir/../dir2/baz.h"

int main() {
    return useNormalInclude() + doBar() + doBaz();
}
