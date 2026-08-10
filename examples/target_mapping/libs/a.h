#include "target_mapping/libs/b.h"
#include "target_mapping/libs/d.h"

int doA() {
    return 42 + doB() + doD();
}
