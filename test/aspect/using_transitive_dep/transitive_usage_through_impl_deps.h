#include "using_transitive_dep/direct_dep.h"
#include "using_transitive_dep/transitive_dep_hdr.h"
// Including a header which is only available from the 'srcs' attribute of a cc_library is wrong. Unfortunately, Bazel
// is not enforcing its own API design regarding this.
// We test this case explicitly to ensure code using this anti pattern can be analyzed by DWYU. Our assumption of use
// is that the code compiles, which this example does.
#include "using_transitive_dep/transitive_dep_src.h"

int doSth() {
    // ERROR: Using a function from library foo but depending only on library bar
    return directDepFn() + transitiveDepFnA() + transitiveDepFnB();
}
