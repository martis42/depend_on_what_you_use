#if FOO == 1
#include "foo.h"
#endif

#if BAR == 1
#include "bar1.h"
#elif BAR == 2
#include "bar2.h"
#else
#include "nobar.h"
#endif

#if BAZ != 3
#include "baz_is_not_3.h"
#endif
