#include "test/using_transitive_dep/foo.h"
#include "test/using_transitive_dep/bar.h"

int main()
{
    // ERROR: Using a function from library foo but depending only on library bar
    const int answer = theAnswer();
    const int stuff = doStuff();
    return answer != stuff;
}
