#include "ext_b.h"
#include "target_mapping/libs/a.h"
#include "target_mapping/libs/b.h"

int main() {
    return doA() + doB() + doExtB();
}
