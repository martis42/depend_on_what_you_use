"""
List is based on https://en.cppreference.com/w/cpp/header.
The content of the website has been copied into a file (plain ctrl + c)
and then extract_std_headers.py has been executed on the file.

The list is a superset of all headers, no matter in which standard they have been introduced
or if they are already removed. If you require a list tailored to a specific standard,
you have to define it yourself and provide it to the tool through the CLI.
"""

# extracted 2022.01.03
STD_HEADER = {
    # concepts
    "concepts",
    # coroutines
    "coroutine",
    # utilities - generic
    "any",
    "bitset",
    "chrono",
    "compare",
    "csetjmp",
    "csignal",
    "cstdarg",
    "cstddef",
    "cstdlib",
    "ctime",
    "functional",
    "initializer_list",
    "optional",
    "source_location",
    "stacktrace",
    "tuple",
    "type_traits",
    "typeindex",
    "typeinfo",
    "utility",
    "variant",
    "version",
    # utilities - dynamic memory management
    "memory",
    "memory_resource",
    "new",
    "scoped_allocator",
    # utilities - numeric limits
    "cfloat",
    "cinttypes",
    "climits",
    "cstdint",
    "limits",
    # utilities - error handling
    "cassert",
    "cerrno",
    "exception",
    "stdexcept",
    "system_error",
    # strings
    "cctype",
    "charconv",
    "cstring",
    "cuchar",
    "cwchar",
    "cwctype",
    "format",
    "string",
    "string_view",
    # containers
    "array",
    "deque",
    "forward_list",
    "list",
    "map",
    "queue",
    "set",
    "span",
    "stack",
    "unordered_map",
    "unordered_set",
    "vector",
    # iterators
    "iterator",
    # ranges
    "ranges",
    # algorithms
    "algorithm",
    "execution",
    # numerics
    "bit",
    "cfenv",
    "cmath",
    "complex",
    "numbers",
    "numeric",
    "random",
    "ratio",
    "valarray",
    # localization
    "clocale",
    "codecvt",
    "locale",
    # input/output
    "cstdio",
    "fstream",
    "iomanip",
    "ios",
    "iosfwd",
    "iostream",
    "istream",
    "ostream",
    "spanstream",
    "sstream",
    "streambuf",
    "strstream",
    "syncstream",
    # filesystem
    "filesystem",
    # regular expression
    "regex",
    # atomic operations
    "atomic",
    # thread support
    "barrier",
    "condition_variable",
    "future",
    "latch",
    "mutex",
    "semaphore",
    "shared_mutex",
    "stop_token",
    "thread",
    # C compatibility headers
    "assert.h",
    "ctype.h",
    "errno.h",
    "fenv.h",
    "float.h",
    "inttypes.h",
    "limits.h",
    "locale.h",
    "math.h",
    "setjmp.h",
    "signal.h",
    "stdarg.h",
    "stddef.h",
    "stdint.h",
    "stdio.h",
    "stdlib.h",
    "string.h",
    "time.h",
    "uchar.h",
    "wchar.h",
    "wctype.h",
    # special C compatibility headers
    "stdatomic.h",
    # Empty C headers
    "ccomplex",
    "complex.h",
    "ctgmath",
    "tgmath.h",
    # Meaningless C headers
    "ciso646",
    "cstdalign",
    "cstdbool",
    "iso646.h",
    "stdalign.h",
    "stdbool.h",
}
