#include "using_transitive_dep/foo.h"
#include "using_transitive_dep/bar.h"

int doSth() {
    // ERROR: Using a function from library foo but depending only on library bar
    const int answer = theAnswer();
    const int stuff = doStuff();
    return answer != stuff;
}
