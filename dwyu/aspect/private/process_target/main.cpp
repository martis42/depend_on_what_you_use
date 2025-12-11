#include "dwyu/private/program_options.h"
#include "dwyu/private/utils.h"

#include <nlohmann/json.hpp>

#include <fstream>
#include <iostream>
#include <string>
#include <utility>
#include <vector>

namespace dwyu {
namespace {

struct ProgramOptions {
    std::string target{};
    std::string output{};
    std::vector<std::string> header_files{};
    std::vector<std::string> includes{};
    std::vector<std::string> quote_includes{};
    std::vector<std::string> external_includes{};
    std::vector<std::string> system_includes{};
    std::vector<std::string> defines{};
    bool verbose{false};
};

ProgramOptions parseProgramOptions(int argc, ProgramOptionsParser::ConstCharArray argv) {
    ProgramOptions options{};

    ProgramOptionsParser parser{};
    // Target which is being analyzed
    parser.addOptionValue("--target", options.target);
    // Stores the output in this file
    parser.addOptionValue("--output", options.output);
    // Header files associated with the target
    parser.addOptionList("--header_files", options.header_files);
    // Include paths available to the compiler
    parser.addOptionList("--includes", options.includes);
    // Include paths available to the compiler for quoted include statements
    parser.addOptionList("--quote_includes", options.quote_includes);
    // Include paths available to the compiler for include statements pointing to headers from external targets
    parser.addOptionList("--external_includes", options.external_includes);
    // Include paths available to the compiler for system include statements
    parser.addOptionList("--system_includes", options.system_includes);
    // Defines for this target
    parser.addOptionList("--defines", options.defines);
    // Print debugging information
    parser.addOptionFlag("--verbose", options.verbose);
    parser.parseOptions(argc, argv);

    return options;
}

void printOptions(const ProgramOptions& options) {
    std::cout << "\nAnalyzing dependency " << options.target << "\n";
    std::cout << "Output               " << options.output << "\n";
    std::cout << "Header files         " << listToStr(options.header_files) << "\n";
    std::cout << "Includes             " << listToStr(options.includes) << "\n";
    std::cout << "Quote includes       " << listToStr(options.quote_includes) << "\n";
    std::cout << "External includes    " << listToStr(options.external_includes) << "\n";
    std::cout << "System includes      " << listToStr(options.system_includes) << "\n";
    std::cout << "Defines              " << listToStr(options.defines) << "\n";
}

} // namespace
} // namespace dwyu

int main(int argc, char* argv[]) {
    auto options = dwyu::parseProgramOptions(argc, argv);

    if (options.verbose) {
        dwyu::printOptions(options);
    }

    nlohmann::json json{};
    json["target"] = std::move(options.target);
    json["header_files"] = std::move(options.header_files);
    json["includes"] = std::move(options.includes);
    json["quote_includes"] = std::move(options.quote_includes);
    json["external_includes"] = std::move(options.external_includes);
    json["system_includes"] = std::move(options.system_includes);
    json["defines"] = std::move(options.defines);

    std::ofstream output{options.output};
    if (output.is_open()) {
        output << json;
        output.close();
    }
    else {
        dwyu::abortWithError("Unable to open output file '", options.output, "'");
    }

    return 0;
}
