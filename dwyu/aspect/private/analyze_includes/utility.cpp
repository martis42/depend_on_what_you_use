#include "dwyu/aspect/private/analyze_includes/utility.h"

#include <boost/filesystem/operations.hpp>
#include <boost/filesystem/path.hpp>
#include <nlohmann/json.hpp>

#include <fstream>
#include <stdexcept>
#include <string>

namespace bfs = boost::filesystem;

namespace dwyu {

nlohmann::json readJsonFromFile(const std::string& path, const bool no_error_on_missing_file) {
    const auto file_path = bfs::path{path};
    if (!bfs::exists(file_path)) {
        if (no_error_on_missing_file) {
            return nlohmann::json{};
        }
        throw std::invalid_argument{"Provided file does not exist: " + path};
    }

    std::ifstream file{path};
    return nlohmann::json::parse(file);
}

} // namespace dwyu
