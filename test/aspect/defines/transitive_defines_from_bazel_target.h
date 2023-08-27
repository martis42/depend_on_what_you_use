// Define introduced through target on which we depend. The target uses the attribute 'defines' which is propagated to
// all users of the target.
#ifdef TRANSITIVE_DEFINE
#include "test/aspect/defines/support/a.h"
#else
#include "test/aspect/defines/support/b.h"
#endif

#include "test/aspect/defines/support/a.h"
#include <vector>

// The following defines shall never be active as they are set though Bazel target attributes 'copts' and
// 'local_defines' which should not leak to users of the target

#ifdef LOCAL_DEFINE
#include "test/aspect/defines/support/b.h"
#endif

#ifdef LOCAL_COPT
#include "test/aspect/defines/support/b.h"
#endif
