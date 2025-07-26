#define INTERNAL

#ifdef INTERNAL
#include "has_internal.h"
#else
#include "no_internal.h"
#endif

#ifdef FOO
#include "has_foo.h"
#else
#include "no_foo.h"
#endif

/*
#ifdef FOO
#include "should_never_be_active_due_to_being_commented"
#else
#include "should_never_be_active_due_to_being_commented"
#endif
*/

#ifndef BAR
#include "no_bar.h"
#else
#include "has_bar.h"
#endif

#if BAZ > 40
#include "baz_greater_40.h"
#elif BAZ > 10
#include "baz_greater_10.h"
#else
#include "no_baz.h"
#endif
