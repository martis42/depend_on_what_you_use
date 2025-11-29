#include "dwyu/aspect/private/preprocessing/extract_includes.h"
#include "dwyu/private/program_options.h"
#include "dwyu/private/utils.h"

#include <nlohmann/json.hpp>

#include <fstream>
#include <iostream>
#include <string>
#include <vector>

namespace dwyu {

struct ProgramOptions {
    std::vector<std::string> files{};
    std::string output{};
    bool verbose{false};
};

ProgramOptions parseProgramOptions(int argc, char* argv[]) {
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

} // namespace dwyu

int main(int argc, char* argv[]) {
    const auto options = dwyu::parseProgramOptions(argc, argv);
    if (options.verbose) {
        std::cout << "Preprocessing : " << dwyu::listToStr(options.files) << "\n";
    }

    auto output_json = nlohmann::json::array();
    for (const auto& file : options.files) {
        std::ifstream input{file};
        if (!input.is_open()) {
            dwyu::abortWithError("Could not open input file '", file, "'");
        }

        const auto included_files = dwyu::extractIncludes(input);

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
