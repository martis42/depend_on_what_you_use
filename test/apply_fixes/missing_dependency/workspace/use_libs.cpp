#include "libs/foo.h"
#include "libs/sub/bar.h"
#include "root_lib.h"

int main() {
    return doFoo() + doBar() + doRoot();
}
