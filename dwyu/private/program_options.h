#ifndef DWYU_PRIVATE_PROGRAM_OPTIONS_H
#define DWYU_PRIVATE_PROGRAM_OPTIONS_H

#include <cstdint>
#include <functional>
#include <map>
#include <memory>
#include <string>
#include <vector>

namespace dwyu {
namespace detail {

struct ProgramOption;

}

// Our requirements towards command line options parsing are:
// - Easy to process a parameter file in one of the formats Bazel can produce:
// https://bazel.build/rules/lib/builtins/Args#set_param_file_format
// - C++11 still supported
// - Modern C++ API
// - Efficiency, as one of our tools simply transform CLI input to files (e.g. no copying of data just for convenience)
// - No for elaborate features as our tools are implementation details. Thus, no need for help text, default values,
// mandatory values, ...
//
// None of the program option libraries we looked at fulfilled all requirements.
// Since, we require only basic parsing logic, we implement our own parser tailored to our exact needs.
class ProgramOptionsParser {
  public:
    // NOLINTNEXTLINE(cppcoreguidelines-avoid-c-arrays) Needed to interact with argv of main(...)
    using ConstCharArray = const char* const[];

    void addOptionFlag(std::string option, bool& target);
    void addOptionValue(std::string option, std::string& target);
    void addOptionList(std::string option, std::vector<std::string>& target);

    // Given the CLI input, extract the options specified through calling the 'add..' functions.
    void parseOptions(int argc, ConstCharArray argv);

  private:
    void parseOptionsfromCommandLine(int argc, ConstCharArray argv);
    void parseOptionsfromParamFile(const std::string& param_file);
    void parseOptionsImpl(const std::function<bool(std::string&)>& get_arg);

    std::map<std::string, std::unique_ptr<detail::ProgramOption>> options_;
};

namespace detail {

struct ProgramOption {
    enum class Type : std::uint_fast8_t {
        Flag,
        Value,
        List,
    };

    explicit ProgramOption(Type type) : type_{type} {}

    ProgramOption(const ProgramOption&) = default;
    ProgramOption(ProgramOption&&) = default;
    ProgramOption& operator=(const ProgramOption&) = default;
    ProgramOption& operator=(ProgramOption&&) = default;

    virtual ~ProgramOption() = default;

    virtual void setValue(std::string arg) = 0;

    Type getType() const { return type_; }

  protected:
    // NOLINTNEXTLINE(cppcoreguidelines-non-private-member-variables-in-classes) Derived classes need access
    Type type_;
};

} // namespace detail

} // namespace dwyu

#endif
