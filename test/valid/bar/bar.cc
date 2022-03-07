#include "private_a.h"
#include "sub/dir/private_b.h"
#include "test/valid/bar/bar.h"
#include "test/valid/foo/b.h"
#include "test/valid/foo/textual.cc"

int doBar()
{
    return doB() + doPrivateA() + doPrivateB();
}
