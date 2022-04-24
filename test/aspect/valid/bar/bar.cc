#include "private_a.h"
#include "sub/dir/private_b.h"
#include "test/aspect/valid/bar/bar.h"
#include "test/aspect/valid/foo/b.h"
#include "test/aspect/valid/foo/textual.cc"

int doBar()
{
    return doB() + doPrivateA() + doPrivateB();
}
