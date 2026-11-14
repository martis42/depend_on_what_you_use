#include "foo.h"
#include "generated_external.h"
#include "generated_tree.h/header.h"
#include "some/dir/bar.h"
#include "virtual/prefix/dir/complex_include_a.h"

#if defined(FOO_H) && defined(BAR_H) && defined(GENERATED_EXTERNAL_H) && defined(GENERATED_TREE_H_HEADER_H) &&         \
    defined(SOME_DIR_COMPLEX_INCLUDE_A_H)
#include "preprocessing/support/lib_a.h"
#else
#include "preprocessing/support/transitive.h"
#endif
