#include <dir/complex_include_a.h>
#include "virtual/prefix/dir/complex_include_b.h"

int useComplexIncludes()
{
    return doComplexIncludeA() + doComplexIncludeB();
}
