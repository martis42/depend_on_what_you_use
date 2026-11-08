#include "foo.h"
#include "ignore_external_dependencies/bridge.h"

int transitiveExternal() {
    return doFoo();
}
