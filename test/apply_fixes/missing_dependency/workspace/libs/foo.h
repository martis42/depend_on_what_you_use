// Show that multiple files 'foo.h' in the dependency graph are no issue
#include "other_lib/foo.h"

int doFoo() {
    return doOtherFoo() + 1337;
}
