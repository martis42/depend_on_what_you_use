#include "virtual/prefix/dir/complex_include_b.h"
#include <dir/complex_include_a.h>

#if defined(COMPLEX_INCLUDE_A_H) && defined(COMPLEX_INCLUDE_B_H)
#include "preprocessing/support/lib_a.h"
#else
#include "preprocessing/support/transitive.h"
#endif
