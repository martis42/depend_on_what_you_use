#ifndef FOO_H
#define FOO_H

// normal relative include to file in same directory
#include "bar.h"
// Enter parent directory and descend again into current directory
#include "../dir/bar.h"
// Relative include to a file in another directory
#include "../dir2/baz.h"
// Example for complex relative path
#include "../../sub/dir2/../dir/bar.h"

inline int doFoo() {
    return doBar() + doBaz();
}

#endif
