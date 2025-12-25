#include "dwyu/aspect/private/analyze_includes/include_statement.h"

#include <nlohmann/json.hpp>

#include <fstream>
#include <string>
#include <utility>
#include <vector>

using json = nlohmann::json;

namespace dwyu {

std::vector<IncludeStatement> getIncludeStatements(const std::vector<std::string>& files) {
    std::vector<IncludeStatement> include_statements{};

    for (const auto& file_path : files) {
        std::ifstream file{file_path};
        const auto data = json::parse(file);

        for (const auto& per_file_data : data) {
            for (const auto& include_data : per_file_data["resolved_includes"]) {
                IncludeStatement include_stmt{};

                include_stmt.file = per_file_data["file"].get<std::string>();
                include_stmt.include = include_data["include"].get<std::string>();
                include_stmt.included_file = include_data["file"].get<std::string>();

                include_statements.push_back(std::move(include_stmt));
            }
        }
    }

    return include_statements;
}

} // namespace dwyu
