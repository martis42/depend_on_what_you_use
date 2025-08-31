#ifndef DWYU_PRIVATE_PROGRAM_OPTIONS_H
#define DWYU_PRIVATE_PROGRAM_OPTIONS_H

#include <memory>
#include <string>
#include <vector>

namespace dwyu {

using CliArgs = std::vector<std::string>;

struct ProgramOption {
    explicit ProgramOption(std::string name) : name_{std::move(name)} {}
    virtual ~ProgramOption() = default;

    // Extract the desired value from a specific part of the CLI arguments. Abort on encountering a problem.
    virtual void readValue(CliArgs& args, std::size_t& idx) = 0;

    std::string getName() { return name_; }

  protected:
    std::string name_;
};

// We implement our own command line parsing lib instead of using an established one.
// Our C++ tools are all implementation details with mostly static usage patterns. Thus, we do not need elaborate help
// text rendering or complex features to build up a user friendly CLI.
//
// We can't reuse boost::program_options, as it cannot parse the files produced by
// https://bazel.build/rules/lib/builtins/Args#set_param_file_format.
// Abseil would be able to do so, but its API does not appeal to us and they already require C++17 as minim version.
//
// Since, a basic command line parser is easy enough, we use our own to not introduce a new dependency to DWYU for a
// trivial functionality and to prevent further constraints regarding minimal supported Bazel version or C++ version.
// The key design points are:
// - Support accepting parameter files instead of command line options
// - Rejects unknown options
// - Options have to appear in a specific order
// - There is no concept of mandatory options, aka there is nofailure if an option is omitted
class ProgramOptionsParser {
  public:
    using ConstCharArray = const char* const[];

    // If the option does not exist, this equals a false value. If he option is found, the value is true.
    void addFlagOption(std::string option, bool& target);
    // The option has to exist and provide a non empty value, otherwise an error is reported.
    void addValueOption(std::string option, std::string& target);
    // The option has to exist, otherwise an error is reported. Empty lists are accepted.
    void addListOption(std::string option, std::vector<std::string>& target);

    // Given the CLI input, extract the requested options. Options are expected to appear in the order in which they
    // have been specified with the 'add..' functions.
    void parseOptions(int argc, ConstCharArray argv);

  private:
    // Abstract away the difference of raw CLI arguments versus a parameter ile with arguments by transforming both into
    // a common format for the rest of the parsing logic to work on.
    CliArgs transformInput(int argc, ConstCharArray argv);

    std::vector<std::unique_ptr<ProgramOption>> options_;
};

} // namespace dwyu

#endif
