#include "bar/bar.h"
#include "bar/private_bar.h"

int doBar() {
    return 1337 + doPrivateStuff();
}
