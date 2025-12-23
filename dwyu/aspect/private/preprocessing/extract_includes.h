#ifndef DWYU_ASPECT_PRIVATE_PREPROCESSING_EXTRACT_INCLUDES_H
#define DWYU_ASPECT_PRIVATE_PREPROCESSING_EXTRACT_INCLUDES_H

#include <istream>
#include <set>
#include <string>

namespace dwyu {

// From the content of a given file extract the file part of all include statements which are not commented out.
// The file part of the include statement includes the quotes or angle brackets.
std::set<std::string> extractIncludes(std::istream& stream);

} // namespace dwyu

#endif
