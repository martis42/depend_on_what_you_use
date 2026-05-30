#ifndef DWYU_CC_ASPECT_PRIVATE_PREPROCESSING_WAVE_GATHER_DIRECT_INCLUDES_HOOK_H
#define DWYU_CC_ASPECT_PRIVATE_PREPROCESSING_WAVE_GATHER_DIRECT_INCLUDES_HOOK_H

#include "dwyu/cc/aspect/private/preprocessing/lib/included_file.h"
#include "dwyu/cc/aspect/private/preprocessing/wave/preprocessing_hook_base.h"

#include <boost/filesystem/operations.hpp>
#include <boost/filesystem/path.hpp>
#include <boost/wave/preprocessing_hooks.hpp>

#include <cstdint>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

namespace dwyu {

// Recursively preprocess all resolvable includes statements, aka includes for which we can locate a file. If a
// include statement cannot be resolved, we assume this include statement is not relevant for our analysis (e.g. a
// CC toolchain header).
// While doing so, we remember the direct include statements of the root file (aka file under inspection) and
// their resolved paths.
// If 'ignore_system_includes' is true, our preprocessing does not recurse into system includes, aka
// includes statements using the '<>' notation.
class GatherDirectIncludesHook : public PreprocessingHooksBase {
  public:
    explicit GatherDirectIncludesHook(const bool ignore_system_includes, std::vector<IncludedFile>& included_files)
        : ignore_system_includes_{ignore_system_includes}, include_depth_{0}, included_files_{included_files},
          working_dir_{boost::filesystem::current_path()} {}

    template <typename ContextT>
    bool locate_include_file(ContextT& ctx,
                             std::string& file_path,
                             bool is_system,
                             char const* current_name,
                             std::string& dir_path,
                             std::string& native_name) {
        // Has to be computed early, since 'locate_include_file' changes 'file_path'
        auto include_statement = makeIncludeStatement(file_path, is_system);

        const bool file_found = boost::wave::context_policies::default_preprocessing_hooks::locate_include_file(
            ctx, file_path, is_system, current_name, dir_path, native_name);

        // If we are in the root file (aka file under inspection) and this is is a relevant include (aka discoverable),
        // then we add it to the list of relevant includes.
        if (include_depth_ == 0 && file_found) {
            included_files_.push_back(
                IncludedFile{std::move(include_statement), makeRelativePath(file_path, working_dir_)});
        }

        if (ignore_system_includes_ && is_system) {
            // Do not recurse into system includes.
            return false;
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
    static std::string makeIncludeStatement(const std::string& file_path, const bool is_system) {
        return is_system ? "<" + file_path + ">" : "\"" + file_path + "\"";
    }

    // NOLINTBEGIN(cppcoreguidelines-use-default-member-init) We prefer initializing all values in one place
    bool ignore_system_includes_;
    std::int32_t include_depth_;
    // NOLINTNEXTLINE(cppcoreguidelines-avoid-const-or-ref-data-members) By design to make values available to caller
    std::vector<IncludedFile>& included_files_;
    boost::filesystem::path working_dir_;
    // NOLINTEND(cppcoreguidelines-use-default-member-init)
};

} // namespace dwyu

#endif
