#ifndef PREPROCESSING_CONDITIONAL_INCLUDES_SUPPORT_LIB_WITH_MACROS_H
#define PREPROCESSING_CONDITIONAL_INCLUDES_SUPPORT_LIB_WITH_MACROS_H

#include "preprocessing/conditional_includes/support/lib_with_macros_nested.h"

#define DEP_HEADER_MACRO

#define DEP_HEADER_LIB_PATH "preprocessing/support/lib_c.h"

// Macros of this header can depend on defines of the target including it
#ifdef CONSUMER_DEFINE
#define DEP_HEADER_CONDITIONAL_MACRO
#endif

#endif // PREPROCESSING_CONDITIONAL_INCLUDES_SUPPORT_LIB_WITH_MACROS_H
