#ifndef DWYU_ASPECT_PRIVATE_PREPROCESSING_PREPROCESSING_HOOKS_H
#define DWYU_ASPECT_PRIVATE_PREPROCESSING_PREPROCESSING_HOOKS_H

#include <boost/wave/preprocessing_hooks.hpp>

#include <set>
#include <string>

namespace dwyu {

bool isSystemInclude(const std::string& include_statement) {
    return !include_statement.empty() && (*include_statement.begin() == '<') && (*include_statement.rbegin() == '>');
}

std::string includeWithoutQuotes(const std::string& include_statement) {
    if ((include_statement.size() >= 3) && (((include_statement[0] == '"') && (*include_statement.rbegin() == '"')) ||
                                            ((include_statement[0] == '<') && (*include_statement.rbegin() == '>')))) {
        return include_statement.substr(1, include_statement.size() - 2);
    }
    else {
        return include_statement;
    }
}

/// Base class with behavior common to all our preprocessing modi
struct PreprocessingHooksBase : public boost::wave::context_policies::default_preprocessing_hooks {
    template <typename ContextT, typename ContainerT>
    bool found_warning_directive(ContextT const& ctx, ContainerT const& message) {
        // We don't care about warning directives, aka '#warning "Some msg"'
        return true;
    }

    template <typename ContextT, typename ExceptionT>
    void throw_exception(const ContextT& ctx, const ExceptionT& ex) {
        if (ex.get_severity() == boost::wave::util::severity::severity_remark ||
            ex.get_severity() == boost::wave::util::severity::severity_warning) {
            // We don't care about non critical exceptions, boost::wave reports quite noisily many things
            return;
        }
        boost::wave::context_policies::default_preprocessing_hooks::throw_exception(ctx, ex);
    }
};

/// Extract all include statements for resolvable includes. If a include statement cannot be resolved (aka we cannot
/// find a file it belongs to) we assume this include statement is not relevant for our analysis (e.g. a CC toolchain
/// header).
struct GatherDirectIncludesIgnoringMissingOnes : public PreprocessingHooksBase {
    GatherDirectIncludesIgnoringMissingOnes(std::set<std::string>& included_files)
        : include_depth{0}, included_files{included_files} {}

    // TODO Optimize this by preventing all valid files being located twice by storing the localization result and
    //      then using it in the 'find_include_file()' callback.
    template <typename ContextT>
    bool found_include_directive(const ContextT& ctx, const std::string& filename, bool include_next) {
        const bool is_system = isSystemInclude(filename);
        std::string file_path = includeWithoutQuotes(filename);

        const char* current_file{nullptr}; // only relevant for supporting 'include_next'
        std::string unused_dir_path{};
        if (!ctx.find_include_file(file_path, unused_dir_path, is_system, current_file)) {
            // Do not try to include files we cannot locate
            return true;
        }

        // If we are in the root file (aka file under inspection) and this is is a relevant include (aka discoverable),
        // then add it to the list of relevant includes.
        if (include_depth == 0) {
            included_files.insert(filename);
        }

        // By default include all fils, except some condition above rejected a file
        return false;
    }

    template <typename ContextT>
    void opened_include_file(ContextT const& ctx,
                             std::string const& relname,
                             std::string const& filename,
                             bool is_system_include) {
        ++include_depth;
    }

    template <typename ContextT>
    void returning_from_include_file(ContextT const& ctx) {
        --include_depth;
    }

    std::int32_t include_depth;
    std::set<std::string>& included_files;
};

} // namespace dwyu

#endif // DWYU_ASPECT_PRIVATE_PREPROCESSING_PREPROCESSING_HOOKS_H
