#if __cplusplus != 201703

// If '__cplusplus' would not be set to the expected value, this invalid include would fail in the DWYU analysis
#include "not/existing/dep.h"

#endif
