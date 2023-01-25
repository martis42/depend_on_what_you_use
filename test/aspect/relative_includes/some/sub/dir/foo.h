#ifndef FOO_H
#define FOO_H

#include "bar.h"

inline int doFoo() {
    return doBar() + 13;
}

#endif
