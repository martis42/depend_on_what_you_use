#include "dwyu/aspect/private/analyze_includes/evaluate_includes.h"
#include "dwyu/aspect/private/analyze_includes/ignored_includes.h"
#include "dwyu/aspect/private/analyze_includes/include_statement.h"
#include "dwyu/aspect/private/analyze_includes/result.h"
#include "dwyu/aspect/private/analyze_includes/system_under_inspection.h"
#include "dwyu/private/program_options.h"
#include "dwyu/private/utils.h"

#include <exception>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

namespace dwyu {
namespace {

struct ProgramOptions {
    std::string output{};
    std::string target_under_inspection{};
    std::vector<std::string> preprocessed_public_files{};
    std::vector<std::string> preprocessed_private_files{};
    std::vector<std::string> deps{};
    std::vector<std::string> implementation_deps{};
    std::string ignored_includes_config{};
    bool optimize_implementation_deps{};
    bool verbose{false};
};

ProgramOptions parseProgramOptions(int argc, ProgramOptionsParser::ConstCharArray argv) {
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

int main_impl(const ProgramOptions& options) {
    const auto ignored_includes = getIgnoredIncludes(options.ignored_includes_config);
    auto system_under_inspection =
        getSystemUnderInspection(options.target_under_inspection, options.deps, options.implementation_deps);
    auto public_includes = getIncludeStatements(options.preprocessed_public_files, ignored_includes);
    auto private_includes = getIncludeStatements(options.preprocessed_private_files, ignored_includes);

    const auto result = evaluateIncludes(public_includes, private_includes, system_under_inspection,
                                         options.optimize_implementation_deps);

    if (!result.isOk()) {
        std::cout << result.toString(options.output) << "\n";
    }

    std::ofstream output{options.output};
    if (output.is_open()) {
        output << result.toJson();
        output.close();
    }
    else {
        dwyu::abortWithError("Unable to open output file '", options.output, "'");
    }

    return result.isOk() ? 0 : 1;
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
