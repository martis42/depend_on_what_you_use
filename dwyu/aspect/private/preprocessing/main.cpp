#include "dwyu/aspect/private/preprocessing/preprocessing_hooks.h"
#include "dwyu/private/program_options.h"
#include "dwyu/private/utils.h"

#include <boost/wave/cpp_context.hpp>
#include <boost/wave/cpp_exceptions.hpp>
#include <boost/wave/cpplexer/cpp_lex_iterator.hpp>
#include <boost/wave/cpplexer/cpp_lex_token.hpp>
#include <nlohmann/json.hpp>

#include <iostream>
#include <set>
#include <string>

namespace dwyu {

struct ProgramOptions {
    std::vector<std::string> files{};
    std::string output{};
    std::vector<std::string> include_paths{};
    std::vector<std::string> system_include_paths{};
    std::vector<std::string> defines{};
    bool verbose{false};
};

ProgramOptions parseProgramOptions(int argc, char* argv[]) {
    ProgramOptions options{};
    ProgramOptionsParser parser{};

    // Files which we are preprocessing
    parser.addOptionList("--files", options.files);
    // Stores the discovered includes in this file
    parser.addOptionValue("--output", options.output);
    // Include paths relevant for discovering included headers
    parser.addOptionList("--include_paths", options.include_paths);
    // Include paths relevant for discovering included headers for system include statements using the '<>' notation
    parser.addOptionList("--system_include_paths", options.system_include_paths);
    // Macros defined by the CC toolchain or the user
    parser.addOptionList("--defines", options.defines);
    // Print debugging information
    parser.addOptionFlag("--verbose", options.verbose);

    parser.parseOptions(argc, argv);

    return options;
}

// Prepare a string representation of the file under inspection as desired by boost::wave::context
std::string makeContextInput(const std::string& file) {
    std::ifstream instream{file};
    if (!instream.is_open()) {
        abortWithError("Could not open input file '", file, "'");
    }
    instream.unsetf(std::ios::skipws);
    return std::string{std::istreambuf_iterator<char>(instream.rdbuf()), std::istreambuf_iterator<char>()};
}

template <typename ContextT>
void resetMacro(ContextT& ctx, const std::string& macro) {
    const auto position_equal_sign = macro.find("=");
    if (position_equal_sign == std::string::npos) {
        // Basic define without value
        ctx.remove_macro_definition(macro, true, true);
    }
    else {
        // Define with value, e.g. 'FOO=42'
        ctx.remove_macro_definition(macro.substr(0, position_equal_sign), true, true);
    }
}

template <typename ContextT>
void configureContext(const ProgramOptions& options, ContextT& ctx) {
    // A lot of code exists which has no newline at the end and all established compilers are able to handle this
    ctx.set_language(boost::wave::language_support::support_option_no_newline_at_end_of_file, true);

    // Since we require C++11 as minimum to compile our own tool and C++11 is mostly the established minimum standard
    // nowadays, setting C++11 as language seems like a sane default.
    // If a projects wants to user newer C++ versions and they are relevant for preprocessing, they can set
    // '__cplusplus' to communicate this to the preprocessor.
    ctx.set_language(boost::wave::language_support::support_cpp11, true);

    for (const auto& path : options.include_paths) {
        ctx.add_include_path(path.c_str());
    }
    for (const auto& path : options.system_include_paths) {
        ctx.add_sysinclude_path(path.c_str());
    }
    for (const auto& macro : options.defines) {
        // Some macros are set by boost::wave internally. Whenever we receive a macro defined on Bazel level, we
        // want to use this value and not the boost::wave default/heuristic.
        resetMacro(ctx, macro);
        ctx.add_macro_definition(macro, true);
    }
}

/// Execute an already configured boost::wave::context to preprocess a file
template <typename ContextT>
bool preprocessFile(ContextT& ctx) {
    boost::wave::util::file_position_type current_position{};
    try {
        auto first = ctx.begin();
        auto last = ctx.end();
        for (; first != last; ++first) {
            current_position = (*first).get_position();
            // Uncomment for detailed debugging of what happens during preprocessing
            // std::cout << (*first).get_value();
        }
        return true;
    } catch (boost::wave::cpp_exception const& ex) {
        std::cerr << "ERROR: Caught 'boost::wave::cpp_exception':\n";
        std::cerr << ex.file_name() << ":" << ex.line_no() << " - " << ex.description() << "\n";
    } catch (std::exception const& ex) {
        std::cerr << "ERROR: Caught 'std::exception':\n";
        std::cerr << current_position.get_file() << ":" << current_position.get_line() << " - " << ex.what() << "\n";
    } catch (...) {
        std::cerr << "ERROR: Caught unknown exception:\n";
        std::cerr << current_position.get_file() << ":" << current_position.get_line() << "\n";
    }
    return false;
}

} // namespace dwyu

int main(int argc, char* argv[]) {
    const auto options = dwyu::parseProgramOptions(argc, argv);
    if (options.verbose) {
        std::cout << "Preprocessing        : " << dwyu::listToStr(options.files) << "\n";
        std::cout << "Include paths        : " << dwyu::listToStr(options.include_paths) << "\n";
        std::cout << "System include paths : " << dwyu::listToStr(options.system_include_paths) << "\n";
        std::cout << "Defines              : " << dwyu::listToStr(options.defines) << "\n";
    }

    auto output_json = nlohmann::json::array();
    for (const auto& file : options.files) {
        auto file_content = dwyu::makeContextInput(file);

        // Define the boost::wave::context class with its default behavior besides using our custom preprocessing hooks
        using token_type = boost::wave::cpplexer::lex_token<>;
        using lex_iterator_type = boost::wave::cpplexer::lex_iterator<token_type>;
        using context_type = boost::wave::context<std::string::iterator, lex_iterator_type,
                                                  boost::wave::iteration_context_policies::load_file_to_string,
                                                  dwyu::GatherDirectIncludesIgnoringMissingOnes>;

        std::set<std::string> included_files{};
        context_type ctx{file_content.begin(), file_content.end(), file.c_str(),
                         dwyu::GatherDirectIncludesIgnoringMissingOnes{included_files}};

        dwyu::configureContext(options, ctx);

        if (dwyu::preprocessFile(ctx) == false) {
            dwyu::abortWithError("Preprocessing failed for file '", file, "'");
        }

        if (options.verbose) {
            std::cout << "\nDiscovered includes:" << "\n";
            for (const auto& inc : included_files) {
                std::cout << "  " << inc << "\n";
            }
            std::cout << "\n";
        }

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
