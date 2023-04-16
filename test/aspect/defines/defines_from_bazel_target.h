#ifdef SOME_DEFINE
#include "test/aspect/defines/lib/a.h"
#else
#include "test/aspect/defines/lib/b.h"
#endif

#ifdef LOCAL_DEFINE
#include "test/aspect/defines/lib/a.h"
#else
#include "test/aspect/defines/lib/b.h"
#endif

#if SOME_COPT > 40
#include "test/aspect/defines/lib/a.h"
#else
#include "test/aspect/defines/lib/b.h"
#endif
