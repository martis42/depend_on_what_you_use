running the preprocessor with "-dI" (gcc and clang support this) allows keeping include statements.
direct includes can be discovered by parsing for pattern:

---
#include "foo/bar.h"
# x "<file_under_inspection>"
---


Woulds also work without -dI by parsing the file bottopm to top and matching

---
# x "<some_header>" x
...
# x "<file_under_inspection>" 2
---

where we match on the first '# ...' above the file_under_inspection line and ignore the rest until the next file_under_inspection line

Or without any elaborate matching on our side
"-H" option will print sth like
---
. c1.h
. ../foo/c2.h
. a.h
.. lib.h
... trans_lib.h
. d.h
---

into the terminal, where ". <some_header>" are direct includes and everything else is transitive
