// Standard library headers are ignored by default without a need for configuration
#include <string>

// Header which does not exist but causes no error due to being ignored explicitly
#include "some/header.h"

// If all headers we want to ignore share a common path we can use patterns in the config to ease maintenance
#include "some_pkg/foo.h"
#include "some_pkg/bar.h"
