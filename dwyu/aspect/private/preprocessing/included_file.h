#ifndef DWYU_ASPECT_PRIVATE_PREPROCESSING_INCLUDED_FILE_H
#define DWYU_ASPECT_PRIVATE_PREPROCESSING_INCLUDED_FILE_H

#include <boost/filesystem/path.hpp>

#include <string>

namespace dwyu {

struct IncludedFile {
    // The file part of the include statement including the quotes or angle brackets
    std::string include_statement;
    // The path of the included file
    std::string resolved_path;
};

// A system include is using angle brackets '<..>'
bool isSystemInclude(const std::string& include_statement);

// Remove angle brackets and quotes from the include statement, if they exist
std::string includeWithoutQuotes(const std::string& include_statement);

// Does not perform any checks. Only call this with valid file paths
std::string makeRelativePath(const std::string& file, const boost::filesystem::path& parent);

} // namespace dwyu

#endif
