#include "test/aspect/interface_deps/b.h"
#include "test/aspect/interface_deps/use_a_and_b.h"

int useB()
{
    return doB() + useA();
}
