#include "dwyu/aspect/private/analyze_includes/ignored_includes.h"

#include "dwyu/aspect/private/analyze_includes/utility.h"
#include "dwyu/aspect/private/preprocessing/included_file.h"

#include <boost/regex.hpp>

#include <algorithm>
#include <string>
#include <tuple>
#include <unordered_set>
#include <vector>

namespace dwyu {

IgnoredIncludes getIgnoredIncludes(const std::string& ignored_includes_config) {
    IgnoredIncludes ignored_includes{};

    constexpr bool no_error_on_missing_file = true;
    const auto ignores_config = readJsonFromFile(ignored_includes_config, no_error_on_missing_file);
    if (ignores_config.contains("ignore_include_paths")) {
        ignored_includes.include_paths = ignores_config["ignore_include_paths"].get<std::unordered_set<std::string>>();
    }
    if (ignores_config.contains("extra_ignore_include_paths")) {
        for (const auto& ignore : ignores_config["extra_ignore_include_paths"]) {
            std::ignore = ignored_includes.include_paths.insert(ignore.get<std::string>());
        }
    }
    if (ignores_config.contains("ignore_include_patterns")) {
        for (const auto& pattern : ignores_config["ignore_include_patterns"].get<std::vector<std::string>>()) {
            ignored_includes.include_patterns.emplace_back(pattern);
        }
    }

    return ignored_includes;
}

bool isIgnoredInclude(const std::string& include, const IgnoredIncludes& ignored_includes) {
    const auto unquoted_include = includeWithoutQuotes(include);

    // Search for full path matches
    if (ignored_includes.include_paths.find(unquoted_include) != ignored_includes.include_paths.end()) {
        return true;
    }

    // Search for pattern matches
    if (std::any_of(ignored_includes.include_patterns.begin(), ignored_includes.include_patterns.end(),
                    [&unquoted_include](const boost::regex& pattern) {
                        return boost::regex_search(unquoted_include, pattern, boost::regex_constants::match_continuous);
                    })) {
        return true;
    }

    return false;
}

} // namespace dwyu
