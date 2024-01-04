#include "defines/support/some_defines.h"

// Set defines based on values from included header

#ifdef SWITCH_USE_B
#define USE_B
#endif

#if SOME_SWITCH_VALUE > 100
#define SOME_VALUE 42
#else
#define SOME_VALUE 0
#endif
