#define AAA

#include "c1.h"
#include "../foo/c2.h"

#ifdef AAA
// some stuff
#include "a.h"
#else
// other stuff
#include "b.h"
#endif

// commn stuff

#include "d.h"