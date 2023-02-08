#if defined(FOO)
#include "foo.h"
#endif

#if !defined(NOBAR)
#include <bar.h>
#else
#include "nobar.h"
#endif

#include <iostream> // a system header
