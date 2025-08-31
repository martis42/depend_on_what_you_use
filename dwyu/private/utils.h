#ifndef DWYU_PRIVATE_UTILS_H
#define DWYU_PRIVATE_UTILS_H

#include <cstdlib>
#include <iostream>
#include <utility>

namespace dwyu {

template <typename T>
void printToError(T&& arg) {
    std::cerr << arg;
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
    std::exit(1);
}

} // namespace dwyu

#endif
