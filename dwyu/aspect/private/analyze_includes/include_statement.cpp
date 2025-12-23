#include "dwyu/aspect/private/analyze_includes/include_statement.h"

#include "dwyu/aspect/private/analyze_includes/ignored_includes.h"

#include <nlohmann/json.hpp>

#include <fstream>
#include <string>
#include <utility>
#include <vector>

namespace dwyu {

std::vector<IncludeStatement> getIncludeStatements(const std::vector<std::string>& files,
                                                   const IgnoredIncludes& ignored_includes) {
    std::vector<IncludeStatement> include_statements{};

    for (const auto& file_path : files) {
        std::ifstream file{file_path};
        const auto data = nlohmann::json::parse(file);

        for (const auto& per_file_data : data) {
            for (const auto& include_data : per_file_data["resolved_includes"]) {
                auto include = include_data["include"].get<std::string>();
                if (!isIgnoredInclude(include, ignored_includes)) {
                    IncludeStatement include_stmt{};
                    include_stmt.file = per_file_data["file"].get<std::string>();
                    include_stmt.include = std::move(include);
                    include_stmt.resolved_include = include_data["file"].get<std::string>();
                    include_statements.push_back(std::move(include_stmt));
                }
            }
        }
    }

    return include_statements;
}

} // namespace dwyu
