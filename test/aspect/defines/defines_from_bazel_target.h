#ifdef SOME_DEFINE
#include "test/aspect/defines/support/a.h"
#else
#include "test/aspect/defines/support/b.h"
#endif

#ifdef LOCAL_DEFINE
#include "test/aspect/defines/support/a.h"
#else
#include "test/aspect/defines/support/b.h"
#endif

#if SOME_COPT > 40
#include "test/aspect/defines/support/a.h"
#else
#include "test/aspect/defines/support/b.h"
#endif
