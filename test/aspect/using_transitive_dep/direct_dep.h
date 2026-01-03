#ifndef USING_TRANSITIVE_DEP_DIRECT_DEP_H
#define USING_TRANSITIVE_DEP_DIRECT_DEP_H

#include "using_transitive_dep/transitive_dep_hdr.h"
#include "using_transitive_dep/transitive_dep_src.h"

int directDepFn() {
    return transitiveDepFnA() + transitiveDepFnB();
}

#endif
