#ifndef DWYU_ASPECT_PRIVATE_ANALYZE_INCLUDES_IGNORED_INCLUDES_H
#define DWYU_ASPECT_PRIVATE_ANALYZE_INCLUDES_IGNORED_INCLUDES_H

#include <boost/regex.hpp>

#include <string>
#include <unordered_set>
#include <vector>

namespace dwyu {

struct IgnoredIncludes {
    // Full paths for include statements which are ignored by the DWYU analysis.
    // Those are compared to the include statement ignoring quotes and angle brackets.
    std::unordered_set<std::string> include_paths{};
    // Regex patterns for include statements which are ignored by the DWYU analysis.
    // Those are compared to the include statement ignoring quotes and angle brackets.
    std::vector<boost::regex> include_patterns{};
};

IgnoredIncludes getIgnoredIncludes(const std::string& ignored_includes_config);

bool isIgnoredInclude(const std::string& include, const IgnoredIncludes& ignored_includes);

} // namespace dwyu

#endif
