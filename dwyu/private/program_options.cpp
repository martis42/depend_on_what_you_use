#include "dwyu/private/program_options.h"
#include "dwyu/private/utils.h"

#include <fstream>

namespace dwyu {
namespace detail {
namespace {

class FlagOption : public ProgramOption {
  public:
    FlagOption(std::string name, bool& target)
        : ProgramOption{std::move(name), ProgramOption::Type::Flag}, target_{target} {
        target_ = false;
    }

    void setValue(std::string arg) override {
        (void)arg;
        target_ = true;
    }

  private:
    bool& target_;
};

struct ValueOption : public ProgramOption {
  public:
    ValueOption(std::string name, std::string& target)
        : ProgramOption{std::move(name), ProgramOption::Type::Value}, target_{target} {}

    void setValue(std::string arg) override { target_ = std::move(arg); }

  private:
    std::string& target_;
};

struct ListOption : public ProgramOption {
  public:
    ListOption(std::string name, std::vector<std::string>& target)
        : ProgramOption{std::move(name), ProgramOption::Type::List}, target_{target} {}

    void setValue(std::string arg) override { target_.push_back(std::move(arg)); }

  private:
    std::vector<std::string>& target_;
};

} // namespace
} // namespace detail

namespace {

bool isOption(const std::string& arg) {
    return arg.size() > 2 && arg[0] == '-' && arg[1] == '-';
}

} // namespace

void ProgramOptionsParser::addOptionFlag(std::string option, bool& target) {
    options_.emplace(std::move(option), std::unique_ptr<detail::FlagOption>(new detail::FlagOption{option, target}));
}

void ProgramOptionsParser::addOptionValue(std::string option, std::string& target) {
    options_.emplace(std::move(option), std::unique_ptr<detail::ValueOption>(new detail::ValueOption{option, target}));
}

void ProgramOptionsParser::addOptionList(std::string option, std::vector<std::string>& target) {
    options_.emplace(std::move(option), std::unique_ptr<detail::ListOption>(new detail::ListOption{option, target}));
}

void ProgramOptionsParser::parseOptions(int argc, ConstCharArray argv) {
    if (options_.empty()) {
        abortWithError("At least a single option is expected to be present");
    }

    if (argc < 2) {
        abortWithError("Expecting at least 2 argv elements");
    }

    const std::string second_arg{argv[1]};
    if (second_arg.compare(0, 13, "--param_file=") == 0) {
        parseOptionsfromParamFile(second_arg.substr(13));
    }
    else {
        parseOptionsfromCommandLine(argc, argv);
    }
}

void ProgramOptionsParser::parseOptionsfromParamFile(const std::string param_file_path) {
    std::ifstream param_file{param_file_path};
    if (param_file) {
        parseOptionsImpl([&param_file](std::string& arg) -> bool {
            if (std::getline(param_file, arg)) {
                return true;
            }
            else {
                return false;
            };
        });
        param_file.close();
    }
    else {
        abortWithError("Could not open param_file '", param_file_path, "'");
    }
}

void ProgramOptionsParser::parseOptionsfromCommandLine(int argc, ConstCharArray argv) {
    int idx{1};
    parseOptionsImpl([&idx, argc, &argv](std::string& arg) -> bool {
        if (idx >= argc) {
            return false;
        }
        else {
            arg = argv[idx];
            ++idx;
            return true;
        }
    });
}

void ProgramOptionsParser::parseOptionsImpl(std::function<bool(std::string&)> get_arg) {
    detail::ProgramOption* active_option{nullptr};
    std::string arg{};
    while (get_arg(arg)) {
        if (isOption(arg)) {
            auto option = options_.find(arg);
            if (option != options_.end()) {
                if (option->second->getType() == detail::ProgramOption::Type::Flag) {
                    option->second->setValue("");
                }
                else {
                    active_option = option->second.get();
                }
            }
            else {
                abortWithError("Received invalid option: '", arg, "'");
            }
        }
        else {
            if (active_option != nullptr) {
                active_option->setValue(std::move(arg));
            }
            else {
                abortWithError("Got a value without it being associated to an option: '", arg, "'");
            }
        }
    }
}

} // namespace dwyu
