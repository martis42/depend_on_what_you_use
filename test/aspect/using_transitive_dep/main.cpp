#include "using_transitive_dep/bar.h"
#include "using_transitive_dep/foo.h"

int main() {
    // ERROR: Using a function from library foo but depending only on library bar
    const int answer = theAnswer();
    const int stuff = doStuff();
    return answer != stuff;
}
