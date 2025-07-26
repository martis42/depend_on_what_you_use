#include "src/aspect/private/analyze_includes/test/data/some_defines.h"

#ifdef MY_DEFINE
#include "expected/include_a.h"
#else
#include "bad/include_a.h"
#endif

#if THE_ANSWER > 40
#include "expected/include_b.h"
#else
#include "bad/include_b.h"
#endif
