#include "dwyu/aspect/private/analyze_includes/include_statement.h"
#include "dwyu/aspect/private/analyze_includes/result.h"
#include "dwyu/aspect/private/analyze_includes/system_under_inspection.h"
#include "dwyu/private/program_options.h"
#include "dwyu/private/utils.h"

#include <nlohmann/json.hpp>

#include <algorithm>
#include <exception>
#include <fstream>
#include <string>
#include <vector>

using json = nlohmann::json;

namespace dwyu {

struct ProgramOptions {
    std::string output{};
    std::string target_under_inspection{};
    std::vector<std::string> preprocessed_public_files{};
    std::vector<std::string> preprocessed_private_files{};
    std::vector<std::string> deps{};
    std::vector<std::string> implementation_deps{};
    std::string ignored_includes_config{};
    std::string toolchain_headers_info{};
    bool optimize_implementation_deps{};
    bool verbose{false};
};

ProgramOptions parseProgramOptions(int argc, char* argv[]) {
    ProgramOptions options{};
    ProgramOptionsParser parser{};

    // Stores the analysis result in this file
    parser.addOptionValue("--output", options.output);
    // Information about target under inspection
    parser.addOptionValue("--target_under_inspection", options.target_under_inspection);
    // Preprocessor results for all public source files of the target under inspection
    parser.addOptionList("--preprocessed_public_files", options.preprocessed_public_files);
    // Preprocessor results for all private source files of the target under inspection
    parser.addOptionList("--preprocessed_private_files", options.preprocessed_private_files);
    // Information about dependencies
    parser.addOptionList("--deps", options.deps);
    // Information about implementation dependencies
    parser.addOptionList("--implementation_deps", options.implementation_deps);
    // Config file in json format specifying which include paths and patterns shall be ignored by the analysis
    parser.addOptionValue("--ignored_includes_config", options.ignored_includes_config);
    // If this is checked, ensure all 'deps' are indeed used in at least one public file
    parser.addOptionFlag("--optimize_implementation_deps", options.optimize_implementation_deps);

    parser.parseOptions(argc, argv);

    return options;
}

std::vector<IncludeStatement>
findIncludesWithoutDirectDependency(const std::vector<IncludeStatement>& includes,
                                    const TargetUsage::Status usage,
                                    const std::unordered_set<std::string>& own_header_files,
                                    SystemUnderInspection::HeadersToDepsMap& direct_deps) {
    std::vector<IncludeStatement> invalid_includes{};

    for (const auto& include : includes) {
        auto dep_hdr_match = direct_deps.find(include.included_file);
        if (dep_hdr_match != direct_deps.end()) {
            for (auto& dep : dep_hdr_match->second) {
                dep->usage.update(usage);
            }
            continue;
        }

        auto self_hdr_match = own_header_files.find(include.included_file);
        if (self_hdr_match != own_header_files.end()) {
            continue;
        }

        invalid_includes.push_back(include);
    }

    return invalid_includes;
}

Result evaluateIncludes(const std::vector<IncludeStatement>& public_includes,
                        const std::vector<IncludeStatement>& private_includes,
                        SystemUnderInspection& system_under_inspection,
                        const bool optimize_impl_deps) {
    Result result{system_under_inspection.target_under_inspection.name, optimize_impl_deps};

    result.setPublicIncludesWithoutDirectDep(findIncludesWithoutDirectDependency(
        public_includes, TargetUsage::Status::Public, system_under_inspection.target_under_inspection.header_files,
        system_under_inspection.headers_to_public_deps_map));
    result.setPrivateIncludesWithoutDirectDep(findIncludesWithoutDirectDependency(
        private_includes, TargetUsage::Status::Private, system_under_inspection.target_under_inspection.header_files,
        system_under_inspection.headers_to_all_deps_map));

    std::vector<std::string> unused_deps{};
    for (const auto& dep_pair : system_under_inspection.headers_to_public_deps_map) {
        for (const auto& dep : dep_pair.second) {
            if (dep->usage.is_used() == false) {
                unused_deps.push_back(dep->name);
            }
        }
    }
    result.setUnusedDeps(std::move(unused_deps));

    // TODO find unused impl deps

    if (optimize_impl_deps) {
        // TODO find wrong usage
    }

    return result;
}

int main_impl(const ProgramOptions& options) {
    std::ignore = options;

    auto system_under_inspection =
        getSystemUnderInspection(options.target_under_inspection, options.deps, options.implementation_deps);
    auto public_includes = getIncludeStatements(options.preprocessed_public_files);
    auto private_includes = getIncludeStatements(options.preprocessed_private_files);

    const auto result = evaluateIncludes(public_includes, private_includes, system_under_inspection,
                                         options.optimize_implementation_deps);

    // TODO impl and execute _filter_empty_dependencies
    // TODO call evaluateIncludes
    // TODO report result

    std::ignore = result;

    return 0;
}

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
