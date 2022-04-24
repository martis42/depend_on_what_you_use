#ifndef USE_LIBS_H
#define USE_LIBS_H

#include "test/aspect/implementation_deps/bar.h"

int wrapBar()
{
    return doBar() * 2;
}

int useLibs();

#endif
