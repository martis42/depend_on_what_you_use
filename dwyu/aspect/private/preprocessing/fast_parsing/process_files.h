#ifndef DWYU_ASPECT_PRIVATE_PREPROCESSING_FAST_PARSING_PROCESS_FILES_H
#define DWYU_ASPECT_PRIVATE_PREPROCESSING_FAST_PARSING_PROCESS_FILES_H

#include <nlohmann/json.hpp>

#include <string>
#include <vector>

namespace dwyu {

nlohmann::json extractIncludesWithFastParsing(const std::vector<std::string>& files,
                                              const std::vector<std::string>& include_paths,
                                              const std::vector<std::string>& system_include_paths,
                                              bool verbose);

}

#endif
