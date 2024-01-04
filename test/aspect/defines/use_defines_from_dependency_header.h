#include "defines/support/conditional_defines.h"

// Analyze include statements based on code parts active due to defines from included header

#ifdef USE_B
#include "defines/support/b.h"
#else
#include "defines/support/c.h"
#endif

#if SOME_VALUE > 40
#include "defines/support/b.h"
#else
#include "defines/support/c.h"
#endif
