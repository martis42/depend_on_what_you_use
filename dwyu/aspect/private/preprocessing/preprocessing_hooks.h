#ifndef DWYU_ASPECT_PRIVATE_PREPROCESSING_PREPROCESSING_HOOKS_H
#define DWYU_ASPECT_PRIVATE_PREPROCESSING_PREPROCESSING_HOOKS_H

#include "dwyu/aspect/private/preprocessing/included_file.h"

#include <boost/filesystem/operations.hpp>
#include <boost/filesystem/path.hpp>
#include <boost/wave/preprocessing_hooks.hpp>

#include <set>
#include <string>
#include <tuple>
#include <utility>

namespace dwyu {

// Base class with behavior common to all our preprocessing modi
struct PreprocessingHooksBase : public boost::wave::context_policies::default_preprocessing_hooks {
    template <typename ContextT, typename ContainerT>
    bool found_warning_directive(ContextT const& ctx, ContainerT const& message) {
        std::ignore = ctx;
        std::ignore = message;

        // We don't care about warning directives, aka '#warning "Some msg"'
        return true;
    }

    template <typename ContextT, typename ContainerT>
    bool found_error_directive(ContextT const& ctx, ContainerT const& message) {
        std::ignore = ctx;
        std::ignore = message;

        // We don't care about error directives, aka '#error "Some msg"'
        //
        // !! This means we might evaluate invalid code paths while preprocessing !!
        //
        // This is not as bad as it sounds. One of our Assumptions of Use is that we analyze valid and compiling code.
        // Thus, we know the code is fine and if we hit an error it is due to us using a wrong configuration.
        //
        // We can't guarantee to know the correct configuration. There are a lot of macros defining how the
        // platform works and what system libraries features are available. Those are mostly not provided via the
        // command line, but determined by the CC toolchain preprocessor and compiler internally. We don't have access
        // to those in DWYU. Various experiments on our side have shown that trying to behave exactly as the compiler
        // is futile or at least requrires an amount of work this hobby project cannot invest.
        //
        // Not ignoring errors would be inconsistent. We, also skip the CC toolchain standard library and system
        // headers during preprocessing because of the problem described above.
        //
        // We consider the impact of this design flaw as low. We are not trying to compile the code. We only preprocess
        // it to find all relevant include statements for the active build configuration. As far as we can tell the
        // likelihood of a conditional include statement in the user's code being based on such a low level compiler
        // internal macro is low. Most conditional include statements are based on macros injected via Bazel to
        // accommodate variation points in the build system. We can handle those without problem, since they are known
        // to Bazel and thus also to us.
        return true;
    }

    template <typename ContextT, typename ExceptionT>
    void throw_exception(const ContextT& ctx, const ExceptionT& ex) {
        // We ignore most exceptions.
        // Remarks and warnings are either way not relevant for us
        // Even errors have to be ignored because they can easily appear due to parsing code with a wrong
        // configuration. For a detailed explanation see the comment in the 'found_error_directive' callback.
        if (ex.get_severity() == boost::wave::util::severity::severity_remark ||
            ex.get_severity() == boost::wave::util::severity::severity_warning ||
            ex.get_severity() == boost::wave::util::severity::severity_error) {
            return;
        }
        boost::wave::context_policies::default_preprocessing_hooks::throw_exception(ctx, ex);
    }
};

// Extract all include statements for resolvable includes. If a include statement cannot be resolved (aka we cannot
// find a file it belongs to) we assume this include statement is not relevant for our analysis (e.g. a CC toolchain
// header).
class GatherDirectIncludesIgnoringMissingOnes : public PreprocessingHooksBase {
  public:
    GatherDirectIncludesIgnoringMissingOnes(std::vector<IncludedFile>& included_files)
        : include_depth_{0}, included_files_{included_files} {
        working_dir_ = boost::filesystem::current_path();
    }

    template <typename ContextT>
    bool locate_include_file(ContextT& ctx,
                             std::string& file_path,
                             bool is_system,
                             char const* current_name,
                             std::string& dir_path,
                             std::string& native_name) {
        std::string include_statement = is_system ? "<" + file_path + ">" : "\"" + file_path + "\"";

        const bool file_found = boost::wave::context_policies::default_preprocessing_hooks::locate_include_file(
            ctx, file_path, is_system, current_name, dir_path, native_name);

        // If we are in the root file (aka file under inspection) and this is is a relevant include (aka discoverable),
        // then we add it to the list of relevant includes.
        if (include_depth_ == 0 && file_found) {
            included_files_.push_back(
                IncludedFile{std::move(include_statement), makeRelativePath(file_path, working_dir_)});
        }

        return file_found;
    }

    template <typename ContextT>
    void opened_include_file(ContextT const& ctx,
                             std::string const& relname,
                             std::string const& filename,
                             bool is_system_include) {
        std::ignore = ctx;
        std::ignore = relname;
        std::ignore = filename;
        std::ignore = is_system_include;

        ++include_depth_;
    }

    template <typename ContextT>
    void returning_from_include_file(ContextT const& ctx) {
        std::ignore = ctx;

        --include_depth_;
    }

  private:
    std::int32_t include_depth_;
    std::vector<IncludedFile>& included_files_;
    boost::filesystem::path working_dir_;
};

} // namespace dwyu

#endif // DWYU_ASPECT_PRIVATE_PREPROCESSING_PREPROCESSING_HOOKS_H
