#include <stdlib.h>

#include <boost/algorithm/string.hpp>
#include <boost/filesystem.hpp>
#include <boost/json.hpp>
#include <boost/program_options.hpp>
#include <boost/system/error_code.hpp>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <unordered_set>
#include <vector>

namespace po = boost::program_options;
namespace json = boost::json;
namespace fs = boost::filesystem;
using namespace boost::algorithm;

std::string readTextFile(const std::string& file_path) {
    std::ifstream file{file_path};
    if (!file.is_open()) {
        std::cerr << "Failed to open file " << file_path << std::endl;
        std::exit(1);
    }

    std::ostringstream oss{};
    oss << file.rdbuf();
    return oss.str();
}

json::value readJsonFile(const std::string& file_path) {
    const auto file_content = readTextFile(file_path);

    boost::system::error_code error{};
    json::value json = json::parse(file_content, error);
    if (error) {
        std::cerr << "Parsing '" << file_path << "' failed with error: " << error.message() << std::endl;
        std::exit(1);
    }

    return json;
}

std::unordered_set<std::string> extractToolchainHeaderFiles(const std::string& file_path) {
    auto json = readJsonFile(file_path);

    constexpr auto section = "header_files";
    if (!(json.is_object() && json.as_object().contains(section) && json.as_object()[section].is_array())) {
        std::cerr << "Json content does not have expected structure:\n" << json << std::endl;
        std::exit(1);
    }

    std::unordered_set<std::string> toolchain_headers{};
    // std::cout << "#######" << std::endl;
    for (auto x : json.as_object()[section].as_array()) {
        toolchain_headers.insert(std::string{x.as_string()});
        // std::cout << x << std::endl;
    }
    // std::cout << "#######" << std::endl;

    return toolchain_headers;

    // TODO make an list of boost file system paths from this and return
}

void extractIncludeSearchPaths(const std::string& file_path) {
    std::ifstream file{file_path};
    std::string line{};
    std::vector<std::string> results{};
    bool inside_include_paths_section{false};
    while (std::getline(file, line)) {
        if (starts_with(line, "#include \"...\" search starts here:")) {
            inside_include_paths_section = true;
            continue;
        }
        if (starts_with(line, "#include <...> search starts here:")) {
            continue;
        }
        if (starts_with(line, "End of search list.")) {
            break;
        }

        if (inside_include_paths_section) {
            results.push_back(line);
        }
    }

    // std::cout << "------" << std::endl;
    // for (auto& x : results) {
    //     std::cout << x << std::endl;
    // }
    // std::cout << "------" << std::endl;
}

std::vector<std::string> extractIncludedHeaders(const std::string& file_path,
                                                const std::unordered_set<std::string>& toolchain_headers) {
    std::ifstream file{file_path};
    std::string line{};
    std::vector<std::string> results{};

    bool inside_include_headers_section{false};
    while (std::getline(file, line)) {
        // rethink early abort properly
        // if (starts_with(line, ". ")) {
        //     inside_include_headers_section = true;
        // } else if (inside_include_headers_section) {
        //     // Finished relevant section
        //     break;
        // }

        if (starts_with(line, ". ") && line.size() > 2) {
            const fs::path path{line.substr(2)};
            // Ensure '/../' parts and leading './' are resolved
            auto normalized = path.lexically_normal().string();
            if (toolchain_headers.find(normalized) == toolchain_headers.end()) {
                results.emplace_back(std::move(normalized));
            }
        }
    }

    // std::cout << "++++++++" << std::endl;
    // for (auto& x : results) {
    //     std::cout << x << std::endl;
    // }
    // std::cout << "++++++++" << std::endl;

    return results;
}

int main(int argc, char* argv[]) {
    // Declare the supported options.
    po::options_description desc("Allowed options");
    desc.add_options()("help", "produce help message");
    desc.add_options()("input", po::value<std::string>(), "TBD");
    desc.add_options()("file", po::value<std::string>(), "TBD");
    desc.add_options()("toolchain_headers_info", po::value<std::string>(), "TBD");
    desc.add_options()("output", po::value<std::string>(), "TBD");

    po::variables_map vm{};
    po::store(po::parse_command_line(argc, argv, desc), vm);
    po::notify(vm);

    if (vm.count("help")) {
        std::cout << desc << std::endl;
        return 1;
    }

    // std::cout << boost::filesystem::path{"./test"}.lexically_normal().string() << std::endl;
    // std::cout << boost::filesystem::path{"test/../bar/tik.txt"}.lexically_normal().string() << std::endl;
    // std::cout << boost::filesystem::path{"test/foo/bar/../tik.txt"}.lexically_normal().string() << std::endl;
    // std::cout << boost::filesystem::path{"../test/foo/bar/../tik.txt"}.lexically_normal().string() << std::endl;

    const auto toolchain_headers = extractToolchainHeaderFiles(vm["toolchain_headers_info"].as<std::string>());
    // extractIncludeSearchPaths(vm["input"].as<std::string>());
    const auto included_headers = extractIncludedHeaders(vm["input"].as<std::string>(), toolchain_headers);

    // const auto included_headers_json = json::value_from(included_headers);
    std::ofstream output{vm["output"].as<std::string>()};
    // output << json::serialize(included_headers_json);
    output << "{\"file\": \"" << vm["file"].as<std::string>() << "\", \"included_headers\": [";
    if (!included_headers.empty()) {
        // TODO modern loop
        for (std::int32_t i{0}; i < included_headers.size() - 1; ++i) {
            output << "\"" << included_headers[i] << "\", ";
        }
        output << "\"" << included_headers.back() << "\"";
    }
    output << "]}";
    output.close();

    return 0;
}
