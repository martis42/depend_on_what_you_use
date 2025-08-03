#include "virtual/prefix/dir/complex_include_b.h"
#include <dir/complex_include_a.h>

int useComplexIncludes() {
    return doComplexIncludeA() + doComplexIncludeB();
}
