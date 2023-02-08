#include <iostream>

#if defined(FOO)
#include "test/aspect/simple_defines/foo.h"
#else
#include "test/aspect/simple_defines/bar.h"
#endif

int main() {
#if defined(FOO)
  int answer = foo();
  std::cout << "Foo enabled, the answer is " << answer << std::endl;
#else
  int answer = bar();
  std::cout << "Bar enabled, the answer is " << answer << std::endl;
#endif
  return 0;
}
