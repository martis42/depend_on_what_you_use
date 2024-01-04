#define USE_A

#ifdef USE_A
#include "defines/support/a.h"
#else
#include "defines/support/b.h"
#endif

#ifdef NON_EXISTING_DEFINE
#include "defines/support/b.h"
#endif

#define SOME_VALUE 42

#if SOME_VALUE > 40
#include "defines/support/a.h"
#else
#include "defines/support/b.h"
#endif
