#include "dwyu/aspect/private/preprocessing/extract_includes.h"
#include "dwyu/private/program_options.h"
#include "dwyu/private/utils.h"

#include <nlohmann/json.hpp>

#include <exception>
#include <fstream>
#include <iostream>
#include <string>
#include <utility>
#include <vector>

namespace dwyu {
namespace {

struct ProgramOptions {
    std::vector<std::string> files{};
    std::string output{};
    bool verbose{false};
};

ProgramOptions parseProgramOptions(int argc, ProgramOptionsParser::ConstCharArray argv) {
    ProgramOptions options{};
    ProgramOptionsParser parser{};

    // Files which we are preprocessing
    parser.addOptionList("--files", options.files);
    // Stores the discovered includes in this file
    parser.addOptionValue("--output", options.output);
    // Print debugging information
    parser.addOptionFlag("--verbose", options.verbose);

    parser.parseOptions(argc, argv);

    return options;
}

int main_impl(const ProgramOptions& options) {
    if (options.verbose) {
        std::cout << "Preprocessing : " << dwyu::listToStr(options.files) << "\n";
    }

    auto output_json = nlohmann::json::array();
    for (const auto& file : options.files) {
        std::ifstream input{file};
        if (!input.is_open()) {
            dwyu::abortWithError("Could not open input file '", file, "'");
        }

        auto included_files = dwyu::extractIncludes(input);

        nlohmann::json entry{};
        entry["file"] = file;
        entry["includes"] = std::move(included_files);
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
