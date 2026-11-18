#include "dwyu/cc/private/program_options.h"
#include "dwyu/cc/private/utils.h"

#include <nlohmann/json.hpp>

#include <exception>
#include <fstream>
#include <iostream>
#include <string>

namespace dwyu {
namespace {

struct ProgramOptions {
    std::string report{};
    std::string output{};
};

ProgramOptions parseProgramOptions(int argc, ProgramOptionsParser::ConstCharArray argv) {
    ProgramOptions options{};
    ProgramOptionsParser parser{};

    // DWYU analysis report of a target
    parser.addOptionValue("--report", options.report);
    // Marker file created if the analysis was successful
    parser.addOptionValue("--output", options.output);

    parser.parseOptions(argc, argv);

    return options;
}

int main_impl(const ProgramOptions& options) {
    std::ifstream report_file{options.report};
    if (!report_file.is_open()) {
        dwyu::abortWithError("Unable to open report file '", options.report, "'");
    }
    const auto report = nlohmann::json::parse(report_file);

    if (!report.at("success").get<bool>()) {
        std::cout << report.at("message").get<std::string>() << "\n";
        return 1;
    }

    std::ofstream output{options.output};
    output << "";
    output.close();
    if (!output) {
        dwyu::abortWithError("Unable to write output file '", options.output, "'");
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
