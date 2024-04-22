#include "lib/a.h"
#include "lib/b.h"

int useLibWithoutDirectDep() {
    return doLibA() + doLibB();
}
