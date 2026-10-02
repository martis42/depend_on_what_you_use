// This header deliberately ends inside an open conditional block.
// The code processing this file is expected to not choke on this and continue working.
// We do not compile this code in the tests, thus breaking the compilation is no problem.
#if defined(SOME_MACRO_THE_TEST_DOES_NOT_DEFINE)
