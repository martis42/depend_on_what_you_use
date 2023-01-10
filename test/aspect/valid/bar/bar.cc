#include "test/aspect/valid/bar/bar.h"

#include "test/aspect/valid/bar/private_a.h"
#include "test/aspect/valid/bar/sub/dir/private_b.h"
#include "test/aspect/valid/foo/b.h"
#include "test/aspect/valid/foo/textual.cc"

int doBar()
{
    return doB() + doPrivateA() + doPrivateB();
}
