#include "dwyu/aspect/private/preprocessing/extract_includes.h"
#include "dwyu/aspect/private/preprocessing/included_file.h"
#include "dwyu/private/program_options.h"
#include "dwyu/private/utils.h"

#include <boost/filesystem/operations.hpp>
#include <boost/wave/util/cpp_include_paths.hpp>
#include <nlohmann/json.hpp>

#include <exception>
#include <fstream>
#include <iostream>
#include <set>
#include <string>
#include <utility>
#include <vector>

namespace bfs = boost::filesystem;
namespace bw = boost::wave;

namespace dwyu {

// NOLINTNEXTLINE(misc-use-anonymous-namespace) Has to be in the namespace of the type
static void to_json(nlohmann::json& data, const IncludedFile& included_file) {
    data = nlohmann::json{{"include", included_file.include_statement}, {"file", included_file.resolved_path}};
}

namespace {

struct ProgramOptions {
    std::vector<std::string> files{};
    std::vector<std::string> include_paths{};
    std::vector<std::string> system_include_paths{};
    std::string output{};
    bool verbose{false};
};

ProgramOptions parseProgramOptions(int argc, ProgramOptionsParser::ConstCharArray argv) {
    ProgramOptions options{};
    ProgramOptionsParser parser{};

    // Files which we are preprocessing
    parser.addOptionList("--files", options.files);
    // Include paths relevant for discovering included headers
    parser.addOptionList("--include_paths", options.include_paths);
    // Include paths relevant for discovering included headers for system include statements using the '<>' notation
    parser.addOptionList("--system_include_paths", options.system_include_paths);
    // Stores the discovered includes in this file
    parser.addOptionValue("--output", options.output);
    // Print debugging information
    parser.addOptionFlag("--verbose", options.verbose);

    parser.parseOptions(argc, argv);

    return options;
}

bw::util::include_paths makeIncludePaths(const ProgramOptions& options) {
    bw::util::include_paths include_paths{};

    for (const auto& path : options.include_paths) {
        include_paths.add_include_path(path.c_str(), false);
    }
    for (const auto& path : options.system_include_paths) {
        include_paths.add_include_path(path.c_str(), true);
    }

    return include_paths;
}

void updateIncludePathsForRelativeIncludes(const std::string& file, bw::util::include_paths& include_paths) {
    // 'set_current_directory(..)' Expects the absolute path to the file under inspection as input.
    const auto abs_path = bfs::absolute(bfs::path{file});
    include_paths.set_current_directory(abs_path.c_str());
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

int main_impl(const ProgramOptions& options) {
    if (options.verbose) {
        std::cout << "Preprocessing        : " << dwyu::listToStr(options.files) << "\n";
        std::cout << "Include paths        : " << dwyu::listToStr(options.include_paths) << "\n";
        std::cout << "System include paths : " << dwyu::listToStr(options.system_include_paths) << "\n";
    }

    const auto working_dir = bfs::current_path();
    auto include_paths = makeIncludePaths(options);
    auto output_json = nlohmann::json::array();

    for (const auto& file : options.files) {
        std::ifstream input{file};
        if (!input.is_open()) {
            dwyu::abortWithError("Could not open input file '", file, "'");
        }

        auto includes = dwyu::extractIncludes(input);
        updateIncludePathsForRelativeIncludes(file, include_paths);

        nlohmann::json entry{};
        entry["file"] = file;
        entry["resolved_includes"] = makeResolvedIncludes(includes, include_paths, working_dir);
        output_json.push_back(std::move(entry));
    }

    std::ofstream output{options.output};
    if (output.is_open()) {
        output << output_json;
        output.close();
    }
    else {
        dwyu::abortWithError("Unable to open output file '", options.output, "'");
    }

    return 0;
}

} // namespace
} // namespace dwyu

int main(int argc, char* argv[]) {
    try {
        return main_impl(dwyu::parseProgramOptions(argc, argv));
    } catch (const std::exception& exception) {
        dwyu::abortWithError("Aborting due to exception: ", exception.what());
    } catch (...) {
        dwyu::abortWithError("Aborting due to an unknown exception");
    }
    return 1;
}
