#ifndef USE_EXTERNAL_LIBS_H
#define USE_EXTERNAL_LIBS_H

#include "foo.h"
#include "some/dir/bar.h"

int useLibs() {
    return doFoo() + doBar();
}

#endif
