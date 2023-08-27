#define USE_A

#ifdef USE_A
#include "test/aspect/defines/support/a.h"
#else
#include "test/aspect/defines/support/b.h"
#endif

#ifdef NON_EXISTING_DEFINE
#include "test/aspect/defines/support/b.h"
#endif

#define SOME_VALUE 42

#if SOME_VALUE > 40
#include "test/aspect/defines/support/a.h"
#else
#include "test/aspect/defines/support/b.h"
#endif
