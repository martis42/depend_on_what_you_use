#include "dwyu/aspect/private/preprocessing/included_file.h"

#include <boost/filesystem/path.hpp>

#include <string>

namespace bfs = boost::filesystem;

namespace dwyu {

bool isSystemInclude(const std::string& include_statement) {
    return !include_statement.empty() && (*include_statement.begin() == '<') && (*include_statement.rbegin() == '>');
}

std::string includeWithoutQuotes(const std::string& include_statement) {
    if ((include_statement.size() >= 3) && (((include_statement[0] == '"') && (*include_statement.rbegin() == '"')) ||
                                            ((include_statement[0] == '<') && (*include_statement.rbegin() == '>')))) {
        return include_statement.substr(1, include_statement.size() - 2);
    }
    return include_statement;
}

std::string makeRelativePath(const std::string& file, const bfs::path& parent) {
    // It is important we use 'generic_string()' to get the portable version using forward slashes.
    // Otherwise, we can't compre those paths to the ones reported by Bazel, which uses the portable format as well.
    return bfs::path{file}.lexically_relative(parent).generic_string();
}

} // namespace dwyu
