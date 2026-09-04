#include "ext_a.h"
#include "target_mapping/libs/a.h"

int doMapped() {
    return 42 + doA() + doExtA();
}
