#include "missing_dependency/workspace/libs/foo.h"
#include "missing_dependency/workspace/libs/sub/bar.h"
#include "missing_dependency/workspace/root_lib.h"

int main() {
    return doFoo() + doBar() + doRoot();
}
