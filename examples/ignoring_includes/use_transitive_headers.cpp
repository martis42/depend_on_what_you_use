// Standard library headers are ignored by default without a need for configuration
#include <string>

// Header for which no direct dependency exists, but causes no error due to being ignored explicitly
#include "ignoring_includes/support/some_header.h"

// If all headers we want to ignore share a common path we can use patterns in the config to ease maintenance
#include "ignoring_includes/support/foo/bar_1.h"
#include "ignoring_includes/support/foo/bar_2.h"

int main() {
    return 0;
}
