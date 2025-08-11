#include <boost/algorithm/string.hpp>
#include <boost/filesystem.hpp>
#include <boost/program_options.hpp>
#include <fstream>
#include <iostream>
#include <stdlib.h>
#include <string>
#include <vector>

namespace {

namespace algo = boost::algorithm;
namespace fs = boost::filesystem;
namespace po = boost::program_options;

po::variables_map parseProgramOptions(int argc, char* argv[]) {
    // clang-format off
    po::options_description options("Allowed options");
    options.add_options()("help",
                          "Produce help message");
    options.add_options()("file_under_inspection",
                          po::value<std::string>(),
                          "Source file we are analyzing");
    options.add_options()("preprocessor_output",
                          po::value<std::string>(),
                          "Preprocessor output listing all included header files");
    options.add_options()("output",
                          po::value<std::string>(),
                          "Json file containing the detected included header files");
    // clang-format on

    po::variables_map vm{};
    po::store(po::parse_command_line(argc, argv, options), vm);
    po::notify(vm);

    if (vm.count("help")) {
        std::cout << options << std::endl;
        std::exit(0);
    }

    return vm;
}

std::vector<std::string> parseGccLikePreprocessorOutput(const std::string& file_path) {
    // We do not know how many included header files we will find. We reserve some capacity in the output vector which
    // is small enough to not matter, even if we reserved too much but still prevents several memory allocations due to
    // the vector growing.
    std::vector<std::string> included_headers{};
    included_headers.reserve(8);

    std::ifstream file{file_path};
    std::string line{};
    bool inside_included_headers_section{false};
    while (std::getline(file, line)) {
        if (algo::starts_with(line, ". ") && line.size() > 2) {
            inside_included_headers_section = true;
            const fs::path path{line.substr(2)};
            // Ensure '/../' parts and leading './' are resolved
            included_headers.emplace_back(path.lexically_normal().string());
        }

        if (inside_included_headers_section && !algo::starts_with(line, ".")) {
            // We are no longer inside the section listing included headers
            break;
        }
    }

    return included_headers;
}

void writeOutput(const std::string& output_file,
                 const std::string& analyzed_file,
                 const std::vector<std::string>& headers) {
    std::ofstream output{output_file};

    output << "{\"file\": \"" << analyzed_file << "\", \"included_headers\": [";
    if (!headers.empty()) {
        for (std::size_t i{0}; i < headers.size() - 1; ++i) {
            output << "\"" << headers[i] << "\", ";
        }
        output << "\"" << headers.back() << "\"";
    }
    output << "]}";

    output.close();
}

} // namespace

int main(int argc, char* argv[]) {
    const auto cli = parseProgramOptions(argc, argv);

    const auto file_under_inspection = cli["file_under_inspection"].as<std::string>();
    const auto preprocessor_output = cli["preprocessor_output"].as<std::string>();
    const auto output_file = cli["output"].as<std::string>();

    const auto included_headers = parseGccLikePreprocessorOutput(preprocessor_output);
    writeOutput(output_file, file_under_inspection, included_headers);

    return 0;
}
