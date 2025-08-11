#include "using_transitive_dep/bar.h"
#include "using_transitive_dep/foo.h"

int main() {
    // ERROR: Using a function from library foo but depending only on library bar
    const int answer = theAnswer();
    const int stuff = doStuff();
    return answer != stuff;
}

// Preprocessor output

// # 0 "using_transitive_dep/main.cpp"
// # 0 "<built-in>"
// # 0 "<command-line>"
// # 1 "/usr/include/stdc-predef.h" 1 3 4
// # 0 "<command-line>" 2
// # 1 "using_transitive_dep/main.cpp"
// # 1 "./using_transitive_dep/bar.h" 1

// # 1 "./using_transitive_dep/foo.h" 1

// int theAnswer() {
//     return 42;
// }
// # 4 "./using_transitive_dep/bar.h" 2

// int doStuff() {
//     return theAnswer() + 1;
// }
// # 2 "using_transitive_dep/main.cpp" 2

// int main() {

//     const int answer = theAnswer();
//     const int stuff = doStuff();
//     return answer != stuff;
// }
