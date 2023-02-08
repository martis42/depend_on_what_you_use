#ifdef FOO
#include "foo.h"
#endif

#ifndef NOBAR
#include "bar.h"
#else
#include "nobar.h"
#endif

#include "baz.h"
