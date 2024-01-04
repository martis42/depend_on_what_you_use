#ifdef SOME_DEFINE
#include "defines/support/a.h"
#else
#include "defines/support/b.h"
#endif

#ifdef LOCAL_DEFINE
#include "defines/support/a.h"
#else
#include "defines/support/b.h"
#endif

#if SOME_COPT > 40
#include "defines/support/a.h"
#else
#include "defines/support/b.h"
#endif
