// relatively including header from own target
#include "system_include.h"
#include "some/sub/dir/foo.h"
// include from virtually prefixed path
#include <sub/dir/bar.h>

int main() {
    return useSystemInclude() + doBar();
}