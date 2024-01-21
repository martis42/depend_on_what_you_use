#ifdef SOME_DEFINE
#include "defines/support/a.h"
#else
#include "non/existing/a.h"
#endif

#ifdef LOCAL_DEFINE
#include "defines/support/a.h"
#else
#include "non/existing/b.h"
#endif

#if SOME_COPT > 40
#include "defines/support/a.h"
#else
#include "non/existing/c.h"
#endif
