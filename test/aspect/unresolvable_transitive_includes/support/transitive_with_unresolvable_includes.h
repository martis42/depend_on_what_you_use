#ifndef TRANSITIVE_WITH_UNRESOLVABLE_INCLUDES_H
#define TRANSITIVE_WITH_UNRESOLVABLE_INCLUDES_H

// These include statements cannot be resolved by the DWYU preprocessing, mimicking CC toolchain headers which are
// deliberately not made available to the preprocessing. The errors raised for them while recursing through the
// header tree are swallowed. This must not influence analyzing the include statements of the file under inspection.
// We don't compile this code in the test, thus the include statements pointing to nothing is no problem.
#include <unresolvable_header_a.h>
#include <unresolvable_header_b.h>

int transitive() {
    return 42;
}

#endif
