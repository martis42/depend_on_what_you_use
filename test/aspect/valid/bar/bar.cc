#include "valid/bar/bar.h"
#include "valid/bar/private_a.h"
#include "valid/bar/sub/dir/private_b.h"
#include "valid/foo/b.h"
#include "valid/foo/textual.cc"

int doBar()
{
    return doB() + doPrivateA() + doPrivateB();
}
