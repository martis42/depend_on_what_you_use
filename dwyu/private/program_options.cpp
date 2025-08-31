#include "dwyu/private/program_options.h"
#include "dwyu/private/utils.h"

#include <fstream>

namespace dwyu {
namespace {

// Not an option name and a valid string
bool isLegalValue(const CliArgs& args, const std::size_t idx) {
    return idx < args.size() && !args[idx].empty() && args[idx][0] != '-';
}

class FlagOption : public ProgramOption {
  public:
    FlagOption(std::string name, bool& target) : ProgramOption{std::move(name)}, target_{target} { target_ = false; }

    void readValue(CliArgs& args, std::size_t& idx) override {
        if (args[idx].compare(name_) == 0) {
            target_ = true;
            ++idx;
        }
        else {
            target_ = false;
            // Do not increment index so next option can try again parsing this part
        }
    }

  private:
    bool& target_;
};

struct ValueOption : public ProgramOption {
  public:
    ValueOption(std::string name, std::string& target) : ProgramOption{std::move(name)}, target_{target} {}

    void readValue(CliArgs& args, std::size_t& idx) override {
        if (args[idx].compare(name_) != 0) {
            abortWithError("Expected option '", name_, "', but got '", args[idx], "'");
        }

        ++idx;
        if (!isLegalValue(args, idx)) {
            abortWithError("Expected value for option '", name_, "', but no argument was provided");
        }
        target_ = std::move(args[idx]);

        ++idx;
    }

  private:
    std::string& target_;
};

struct ListOption : public ProgramOption {
  public:
    ListOption(std::string name, std::vector<std::string>& target) : ProgramOption{std::move(name)}, target_{target} {}

    void readValue(CliArgs& args, std::size_t& idx) override {
        if (args[idx].compare(name_) != 0) {
            abortWithError("Expected option '", name_, "', but got '", args[idx], "'");
        }

        while (true) {
            ++idx;
            if (!isLegalValue(args, idx)) {
                break;
            }
            target_.push_back(std::move(args[idx]));
        }
    }

  private:
    std::vector<std::string>& target_;
};

} // namespace

void ProgramOptionsParser::addFlagOption(std::string option, bool& target) {
    options_.push_back(std::make_unique<FlagOption>(option, target));
}

void ProgramOptionsParser::addValueOption(std::string option, std::string& target) {
    options_.push_back(std::make_unique<ValueOption>(option, target));
}

void ProgramOptionsParser::addListOption(std::string option, std::vector<std::string>& target) {
    options_.push_back(std::make_unique<ListOption>(option, target));
}

void ProgramOptionsParser::parseOptions(int argc, ConstCharArray argv) {
    if (options_.empty()) {
        abortWithError("At least a single option is expected to be present");
    }
    auto args = transformInput(argc, argv);

    std::size_t args_idx{0};
    for (auto& option : options_) {
        option->readValue(args, args_idx);
        if (args_idx >= args.size()) {
            break;
        }
    }
    if (args_idx < args.size()) {
        abortWithError("Processed all expected options, but there is still unprocessed CLI input");
    }
}

CliArgs ProgramOptionsParser::transformInput(int argc, ConstCharArray argv) {
    if (argc < 2) {
        abortWithError("Expecting at least 2 arguments");
    }

    const std::string second_arg{argv[1]};
    if (second_arg.compare(0, 13, "--param_file=") == 0) {
        const auto param_file_path = second_arg.substr(13);
        std::ifstream param_file{param_file_path};
        if (param_file) {
            CliArgs args{};
            // This is a magic number to reduce the amount of system calls for requesting new memory
            // We don't know the upper limit, but we know there will always be some options
            args.reserve(16);
            args.emplace_back("");

            while (std::getline(param_file, args.back())) {
                args.emplace_back("");
            }
            // Remove data from the getline call telling us there is no more content in the file
            args.pop_back();

            param_file.close();
            return args;
        }
        else {
            abortWithError("Could not open param_file '", param_file_path, "'");
        }
    }

    auto start_relevant_options = argv + 1;
    auto num_relevant_options = argc - 1;
    return CliArgs{start_relevant_options, start_relevant_options + num_relevant_options};
}

} // namespace dwyu
