#ifndef DWYU_ASPECT_PRIVATE_ANALYZE_INCLUDES_RESULT_H
#define DWYU_ASPECT_PRIVATE_ANALYZE_INCLUDES_RESULT_H

#include "dwyu/aspect/private/analyze_includes/include_statement.h"

#include <nlohmann/json.hpp>

#include <string>
#include <vector>

namespace dwyu {

class Result {
  public:
    Result(const std::string& target, bool optimize_impl_deps);

    bool isOk() const;

    std::string toString(const std::string& report_path) const;
    nlohmann::json toJson() const;

    void setPublicIncludesWithoutDirectDep(std::vector<IncludeStatement> includes);
    void setPrivateIncludesWithoutDirectDep(std::vector<IncludeStatement> includes);
    void setUnusedDeps(std::vector<std::string> deps);
    void setUnusedImplDeps(std::vector<std::string> deps);
    void setDepsWhichShouldBePrivate(std::vector<std::string> deps);

  private:
    std::string target_;
    // TODO Check if we really need this anymore in the automatic fixes script
    //      Seems like we no longer need this as impl_deps is globally available with Bazel >= 7
    //      and the user either way decides if he wants all fixes or not and if impl_fixes are enabled with the aspect
    bool optimize_impl_deps_;

    std::vector<IncludeStatement> public_includes_without_direct_dep_;
    std::vector<IncludeStatement> private_includes_without_direct_dep_;
    std::vector<std::string> unused_deps_;
    std::vector<std::string> unused_impl_deps_;
    std::vector<std::string> public_dep_which_should_be_private_;
};

} // namespace dwyu

#endif
