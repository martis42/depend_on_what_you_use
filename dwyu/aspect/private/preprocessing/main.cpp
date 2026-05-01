#include "dwyu/aspect/private/preprocessing/fast_parsing/process_files.h"
#include "dwyu/aspect/private/preprocessing/wave/gather_direct_includes_hook.h"
#include "dwyu/aspect/private/preprocessing/wave/process_files.h"
#include "dwyu/private/program_options.h"
#include "dwyu/private/utils.h"

#include <boost/wave/cpp_context.hpp>
#include <boost/wave/cpp_iteration_context.hpp>
#include <boost/wave/cpplexer/cpp_lex_iterator.hpp>
#include <boost/wave/cpplexer/cpp_lex_token.hpp>
#include <nlohmann/json.hpp>

#include <exception>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

namespace dwyu {
namespace {

struct ProgramOptions {
    std::vector<std::string> files{};
    std::string mode{};
    std::vector<std::string> include_paths{};
    std::vector<std::string> system_include_paths{};
    std::vector<std::string> defines{};
    std::string output{};
    bool verbose{false};
};

ProgramOptions parseProgramOptions(const int argc, ProgramOptionsParser::ConstCharArray argv) {
    ProgramOptions options{};
    ProgramOptionsParser parser{};

    // Files which we are preprocessing
    parser.addOptionList("--files", options.files);
    // Decide which preprocessing strategy is used. Possible values are:
    // - 'fast' : Extract all non commented include statements without considering preprocessor condtionals.
    // - 'full' : Use boost::wave to preprocess the file and extract includes from it.
    parser.addOptionValue("--mode", options.mode);
    // Include paths relevant for discovering included headers
    parser.addOptionList("--include_paths", options.include_paths);
    // Include paths relevant for discovering included headers for system include statements using the '<>' notation
    parser.addOptionList("--system_include_paths", options.system_include_paths);
    // Macros defined by the CC toolchain or the user
    parser.addOptionList("--defines", options.defines);
    // Stores the discovered includes in this file
    parser.addOptionValue("--output", options.output);
    // Print debugging information
    parser.addOptionFlag("--verbose", options.verbose);

    parser.parseOptions(argc, argv);

    return options;
}

int main_impl(const ProgramOptions& options) {
    if (options.verbose) {
        std::cout << "\n";
        std::cout << ">> Preprocessing " << listToStr(options.files) << "\n";
        std::cout << "\n";
        std::cout << "Mode                 : " << options.mode << "\n";
        std::cout << "Include paths        : " << listToStr(options.include_paths) << "\n";
        std::cout << "System include paths : " << listToStr(options.system_include_paths) << "\n";
        std::cout << "Defines              : " << listToStr(options.defines) << "\n";
    }

    nlohmann::json output_json{};
    if (options.mode == "full") {
        using token_type = boost::wave::cpplexer::lex_token<>;
        using lex_iterator_type = boost::wave::cpplexer::lex_iterator<token_type>;
        using context_type = boost::wave::context<std::string::iterator, lex_iterator_type,
                                                  boost::wave::iteration_context_policies::load_file_to_string,
                                                  GatherDirectIncludesHook>;
        output_json = extractIncludesWithPreprocessor<context_type, GatherDirectIncludesHook>(
            options.files, options.include_paths, options.system_include_paths, options.defines, options.verbose);
    }
    else if (options.mode == "fast") {
        output_json = extractIncludesWithFastParsing(options.files, options.include_paths, options.system_include_paths,
                                                     options.verbose);
    }
    else {
        abortWithError("Invalid mode '", options.mode, "'. Valid modes are 'fast' and 'full'.");
    }

    std::ofstream output{options.output};
    if (output.is_open()) {
        output << output_json;
        output.close();
    }
    else {
        abortWithError("Unable to open output file '", options.output, "'");
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
