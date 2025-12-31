#ifndef DWYU_PRIVATE_UTILS_H
#define DWYU_PRIVATE_UTILS_H

#include <cstdlib>
#include <iostream>
#include <string>
#include <utility>
#include <vector>

namespace dwyu {

template <typename T>
void printToError(T&& arg) {
    // NOLINTNEXTLINE(cppcoreguidelines-pro-bounds-array-to-pointer-decay)
    std::cerr << std::forward<T>(arg);
}

template <typename T, typename... Args>
void printToError(T&& first, Args&&... rest) {
    printToError(std::forward<T>(first));
    printToError(std::forward<Args>(rest)...);
}

template <typename... Args>
void abortWithError(Args&&... args) {
    std::cerr << "ERROR: ";
    printToError(std::forward<Args>(args)...);
    std::cerr << "\n";
    // NOLINTNEXTLINE(concurrency-mt-unsafe) We are not running multi threaded
    std::exit(1);
}

std::string listToStr(const std::vector<std::string>& list);

} // namespace dwyu

#endif
