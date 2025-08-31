#include "dwyu/private/program_options.h"
#include "dwyu/private/utils.h"

#include <boost/json.hpp>

#include <fstream>
#include <string>
#include <vector>

namespace dwyu {

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

ProgramOptions ParseProgramOptions(int argc, char* argv[]) {
    ProgramOptions options{};

    ProgramOptionsParser parser{};
    parser.addValueOption("--target", options.target);
    parser.addValueOption("--output", options.output);
    parser.addListOption("--header_files", options.header_files);
    parser.addListOption("--includes", options.includes);
    parser.addListOption("--quote_includes", options.quote_includes);
    parser.addListOption("--external_includes", options.external_includes);
    parser.addListOption("--system_includes", options.system_includes);
    parser.addListOption("--defines", options.defines);
    parser.addFlagOption("--verbose", options.verbose);

    parser.parseOptions(argc, argv);

    return options;
}

boost::json::string makeJsonString(const std::string& string) {
    return boost::json::string{string.c_str()};
}

boost::json::array makeJsonArray(const std::vector<std::string>& vector) {
    boost::json::array array{};
    array.reserve(vector.size());

    for (const auto& element : vector) {
        array.push_back(element.c_str());
    }

    return array;
}

std::string optionsToJson(const ProgramOptions& options) {
    boost::json::object json{};
    json["target"] = dwyu::makeJsonString(options.target);
    json["header_files"] = dwyu::makeJsonArray(options.header_files);
    json["includes"] = dwyu::makeJsonArray(options.includes);
    json["quote_includes"] = dwyu::makeJsonArray(options.quote_includes);
    json["external_includes"] = dwyu::makeJsonArray(options.external_includes);
    json["system_includes"] = dwyu::makeJsonArray(options.system_includes);
    json["defines"] = dwyu::makeJsonArray(options.defines);

    return boost::json::serialize(json);
}

} // namespace dwyu

int main(int argc, char* argv[]) {
    const auto options = dwyu::ParseProgramOptions(argc, argv);

    std::ofstream output{options.output};
    if (output.is_open()) {
        output << optionsToJson(options);
        output.close();
    }
    else {
        dwyu::abortWithError("Unable to open output file '", options.output, "'");
    }

    return 0;
}
