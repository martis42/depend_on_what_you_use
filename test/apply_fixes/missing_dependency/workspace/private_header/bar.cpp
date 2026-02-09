#include "missing_dependency/workspace/private_header/bar.h"
#include "missing_dependency/workspace/private_header/private_bar.h"

int doBar() {
    return 1337 + doPrivateStuff();
}
