#include "ambiguous_lib/lib.h"
#include "configured_lib/configured_deps.h"

int useConfiguredLib() {
    return doSomethingConfigured() + doSomething();
}
