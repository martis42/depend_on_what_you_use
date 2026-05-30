#include "dwyu/cc/aspect/private/preprocessing/fast_parsing/process_files.h"
#include "dwyu/cc/aspect/private/preprocessing/wave/gather_direct_includes_hook.h"
#include "dwyu/cc/aspect/private/preprocessing/wave/process_files.h"
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
    // Which preprocessing strategy is being used
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

nlohmann::json extractIncludesFromFiles(const ProgramOptions& options) {

    if (options.mode == "full" || options.mode == "ignore_system_includes") {
        using TokenT = boost::wave::cpplexer::lex_token<>;
        using LexIteratorT = boost::wave::cpplexer::lex_iterator<TokenT>;
        using ContextT = boost::wave::context<std::string::iterator, LexIteratorT,
                                              boost::wave::iteration_context_policies::load_file_to_string,
                                              GatherDirectIncludesHook>;
        const bool ignore_system_includes = options.mode == "ignore_system_includes";
        return extractIncludesWithPreprocessor<ContextT, GatherDirectIncludesHook>(
            options.files, options.include_paths, options.system_include_paths, options.defines, ignore_system_includes,
            options.verbose);
    }
    if (options.mode == "fast") {
        return extractIncludesWithFastParsing(options.files, options.include_paths, options.system_include_paths,
                                              options.verbose);
    }

    abortWithError("Invalid preprocessing mode '", options.mode,
                   "'. Valid modes are 'full', 'ignore_system_includes' and 'fast'.");
    // Cannot be reached, but required to silence compiler warnings about missing return statement
    return {};
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

    auto output_json = extractIncludesFromFiles(options);

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
