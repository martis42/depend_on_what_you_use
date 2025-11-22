#ifndef USE_LIBS_H
#define USE_LIBS_H

#include "implementation_deps/support/lib_a.h"

int wrapBar() {
    return libA() * 2;
}

int useLibs();

#endif
