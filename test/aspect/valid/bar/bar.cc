// Although the best practice is to include headers relative to their workspace root, relative include statements still
// work. Thus, we explicitly test this, even if it is violating Bazel best practices.
#include "private_a.h"
#include "sub/dir/private_b.h"
// Normal includes relative to the worskpace root.
#include "test/aspect/valid/bar/bar.h"
#include "test/aspect/valid/foo/b.h"
#include "test/aspect/valid/foo/textual.cc"

int doBar()
{
    return doB() + doPrivateA() + doPrivateB();
}
