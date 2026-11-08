#include "ignore_external_dependencies/bridge.h"
#include "virtual/prefix/dir/complex_include_a.h"

int virtualHeader() {
    return doComplexIncludeA();
}
