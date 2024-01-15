// Define introduced through target on which we depend. The target uses the attribute 'defines' which is propagated to
// all users of the target.
#ifdef TRANSITIVE_DEFINE
#include "defines/support/a.h"
#else

#include "non/existing/a.h"

#endif

#include "defines/support/a.h"
#include <vector>

// The following defines shall never be active as they are set though Bazel target attributes 'copts' and
// 'local_defines' which should not leak to users of the target

#ifdef LOCAL_DEFINE
#include "non/existing/b.h"
#endif

#ifdef LOCAL_COPT
#include "non/existing/c.h"
#endif
