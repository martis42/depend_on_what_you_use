#include "dwyu/aspect/private/preprocessing/fast_parsing/process_files.h"
#include "dwyu/aspect/private/preprocessing/fast_parsing/extract_includes.h"
#include "dwyu/aspect/private/preprocessing/lib/included_file.h"
#include "dwyu/private/utils.h"

#include <boost/filesystem/operations.hpp>
#include <boost/wave/util/cpp_include_paths.hpp>
#include <nlohmann/json.hpp>

#include <fstream>
#include <iostream>
#include <set>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

namespace dwyu {
namespace {

namespace bfs = boost::filesystem;
namespace bw = boost::wave;

bw::util::include_paths makePreprocessorIncludePaths(const std::vector<std::string>& include_paths,
                                                     const std::vector<std::string>& system_include_paths) {
    bw::util::include_paths pp_include_paths{};

    for (const auto& path : include_paths) {
        constexpr bool is_no_system_include{false};
        std::ignore = pp_include_paths.add_include_path(path.c_str(), is_no_system_include);
    }
    for (const auto& path : system_include_paths) {
        constexpr bool is_system_include{true};
        std::ignore = pp_include_paths.add_include_path(path.c_str(), is_system_include);
    }

    return pp_include_paths;
}

void updateIncludePathsForRelativeIncludes(const std::string& file, bw::util::include_paths& include_paths) {
    // 'set_current_directory(..)' Expects the absolute path to the file under inspection as input.
    const auto abs_path = bfs::absolute(bfs::path{file});
    include_paths.set_current_directory(abs_path.string().c_str());
}

std::vector<IncludedFile> makeResolvedIncludes(const std::set<std::string>& includes,
                                               const bw::util::include_paths& include_paths,
                                               const bfs::path& working_dir) {
    std::vector<IncludedFile> resolved_includes{};
    resolved_includes.reserve(includes.size());

    for (const auto& include : includes) {
        std::string unused_dir_path{};
        // only relevant for supporting 'include_next'
        const char* current_file{nullptr};
        // 'find_include_file()' will set this to the absolute path of the discovered file
        auto file_path = includeWithoutQuotes(include);

        // We ignore files which cannot be found. Those are the headers provided by the Bazel CC toolchain for which
        // we do not perform any dependency analysis
        if (include_paths.find_include_file(file_path, unused_dir_path, isSystemInclude(include), current_file)) {
            resolved_includes.push_back(IncludedFile{include, makeRelativePath(file_path, working_dir)});
        }
    }

    return resolved_includes;
}

} // namespace

// NOLINTNEXTLINE(misc-use-anonymous-namespace) Has to be in the namespace of the type
static void to_json(nlohmann::json& data, const IncludedFile& included_file) {
    data = nlohmann::json{{"include", included_file.include_statement}, {"file", included_file.resolved_path}};
}

nlohmann::json extractIncludesWithFastParsing(const std::vector<std::string>& files,
                                              const std::vector<std::string>& include_paths,
                                              const std::vector<std::string>& system_include_paths,
                                              const bool verbose) {
    const auto working_dir = bfs::current_path();
    auto pp_include_paths = makePreprocessorIncludePaths(include_paths, system_include_paths);

    auto output_json = nlohmann::json::array();
    for (const auto& file : files) {
        std::ifstream input{file};
        if (!input.is_open()) {
            abortWithError("Could not open input file '", file, "'");
        }

        const auto includes = extractIncludes(input);
        updateIncludePathsForRelativeIncludes(file, pp_include_paths);

        const auto resolved_includes = makeResolvedIncludes(includes, pp_include_paths, working_dir);
        if (verbose) {
            std::cout << "\nDiscovered includes:" << (resolved_includes.empty() ? " None" : "") << "\n";
            for (const auto& inc : resolved_includes) {
                std::cout << "  " << inc.include_statement << " - " << inc.resolved_path << "\n";
            }
            std::cout << "\n";
        }

        nlohmann::json entry{};
        entry["file"] = file;
        entry["resolved_includes"] = resolved_includes;
        output_json.push_back(std::move(entry));
    }

    return output_json;
}

} // namespace dwyu
