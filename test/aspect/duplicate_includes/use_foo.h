// clang-format off

// Include the same header multiple times to show the DWYU analysis is not tripped by this
#include "duplicate_includes/foo.h"
#include "duplicate_includes/foo.h"

// Same for CC toolchain headers
#include <string>
#include <string>

// clang-format on
