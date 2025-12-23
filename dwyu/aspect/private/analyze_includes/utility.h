#ifndef DWYU_ASPECT_PRIVATE_ANALYZE_INCLUDES_UTILITY_H
#define DWYU_ASPECT_PRIVATE_ANALYZE_INCLUDES_UTILITY_H

#include <nlohmann/json.hpp>

#include <string>

namespace dwyu {

// path                     : Path to the json file. Throws an exceptions if file does not exist.
// no_error_on_missing_file : Instead of throwing an exception, return an empty json object for missing files.
nlohmann::json readJsonFromFile(const std::string& path, bool no_error_on_missing_file = false);

} // namespace dwyu

#endif
