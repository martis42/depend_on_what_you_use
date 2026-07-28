#ifndef VARIADIC_MACRO_H
#define VARIADIC_MACRO_H

// Invoking this macro without variadic arguments is valid since C++20 and tolerated by all major compilers in
// older language modes. boost::wave raises a 'too few macro arguments' warning for it in C++11 mode.
#define DWYU_TEST_LOG(fmt, ...) fmt

#endif
