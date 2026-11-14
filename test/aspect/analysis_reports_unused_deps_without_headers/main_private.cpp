#include "foo.h"
#include "private.h"

int main() {
    return foo() + private_value();
}
