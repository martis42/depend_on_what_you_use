#define HEADER_PATH_A "defines/support/some_defines.h"

#include HEADER_PATH_A

// Ensure the 'some_define.h' header was included and parsed correctly by using some of its content
#if SOME_SWITCH_VALUE > 100
#include "defines/support/a.h"
#endif

#include CONDITIONAL_DEFINES_HEADER

// Ensure the 'conditional_defines.h' header was included and parsed correctly by using some of its content
#if SOME_VALUE > 40
#include "defines/support/b.h"
#else
