#ifndef DWYU_ASPECT_PRIVATE_PREPROCESSING_EXTRACT_INCLUDES_H
#define DWYU_ASPECT_PRIVATE_PREPROCESSING_EXTRACT_INCLUDES_H

#include <istream>
#include <set>
#include <string>

namespace dwyu {

std::set<std::string> extractIncludes(std::istream& stream);

}

#endif
