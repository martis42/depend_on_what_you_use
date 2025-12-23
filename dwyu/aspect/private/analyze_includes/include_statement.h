#ifndef DWYU_ASPECT_PRIVATE_ANALYZE_INCLUDES_INCLUDE_STATEMENT_H
#define DWYU_ASPECT_PRIVATE_ANALYZE_INCLUDES_INCLUDE_STATEMENT_H

#include <string>
#include <vector>

namespace dwyu {

struct IncludeStatement {
    // The file in which the include statement appears
    std::string file;
    // The file part of the include statement including the quotes or angle brackets
    std::string include;
    // The path of the included file. The path is relative to the Bazel actions execution directory
    std::string included_file;
};

// Parse the result of preprocessing the individual source files of the target under inspection
std::vector<IncludeStatement> getIncludeStatements(const std::vector<std::string>& files);

} // namespace dwyu

#endif
