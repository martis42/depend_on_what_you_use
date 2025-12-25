#include "dwyu/aspect/private/analyze_includes/evaluate_includes.h"

#include <string>
#include <unordered_set>
#include <vector>

namespace dwyu {
namespace {

std::vector<IncludeStatement>
findIncludesWithoutDirectDependency(const std::vector<IncludeStatement>& includes,
                                    const TargetUsage::Status usage,
                                    const std::unordered_set<std::string>& own_header_files,
                                    SystemUnderInspection::HeadersToDepsMap& direct_deps) {
    std::vector<IncludeStatement> invalid_includes{};

    for (const auto& include : includes) {
        auto dep_hdr_match = direct_deps.find(include.included_file);
        if (dep_hdr_match != direct_deps.end()) {
            for (auto& dep : dep_hdr_match->second) {
                dep->usage.update(usage);
            }
            continue;
        }

        auto self_hdr_match = own_header_files.find(include.included_file);
        if (self_hdr_match != own_header_files.end()) {
            continue;
        }

        invalid_includes.push_back(include);
    }

    return invalid_includes;
}

} // namespace

Result evaluateIncludes(const std::vector<IncludeStatement>& public_includes,
                        const std::vector<IncludeStatement>& private_includes,
                        SystemUnderInspection& system_under_inspection,
                        const bool optimize_impl_deps) {
    Result result{system_under_inspection.target_under_inspection.name, optimize_impl_deps};

    auto public_includes_without_direct_dep = findIncludesWithoutDirectDependency(
        public_includes, TargetUsage::Status::Public, system_under_inspection.target_under_inspection.header_files,
        system_under_inspection.headers_to_public_deps_map);
    result.setPublicIncludesWithoutDirectDep(std::move(public_includes_without_direct_dep));

    auto private_includes_without_direct_dep = findIncludesWithoutDirectDependency(
        private_includes, TargetUsage::Status::Private, system_under_inspection.target_under_inspection.header_files,
        system_under_inspection.headers_to_all_deps_map);
    result.setPrivateIncludesWithoutDirectDep(std::move(private_includes_without_direct_dep));

    std::vector<std::string> unused_deps{};
    for (const auto& dep_pair : system_under_inspection.headers_to_public_deps_map) {
        for (const auto& dep : dep_pair.second) {
            if (dep->usage.is_used() == false) {
                unused_deps.push_back(dep->name);
            }
        }
    }
    result.setUnusedDeps(std::move(unused_deps));

    // TODO can we optimize this so it is not performing again and again a find?
    std::vector<std::string> unused_impl_deps{};
    for (const auto& dep_pair : system_under_inspection.headers_to_all_deps_map) {
        for (const auto& dep : dep_pair.second) {
            if (dep->usage.is_used() == false) {
                if (std::find(unused_deps.begin(), unused_deps.end(), dep->name) == unused_deps.end()) {
                    // Only add deps which are not yet reported as unused public deps
                    unused_impl_deps.push_back(dep->name);
                }
            }
        }
    }
    result.setUnusedImplDeps(std::move(unused_impl_deps));

    std::vector<std::string> deps_which_should_be_private{};
    if (optimize_impl_deps) {
        for (const auto& dep_pair : system_under_inspection.headers_to_public_deps_map) {
            for (const auto& dep : dep_pair.second) {
                if (dep->usage.usage() == TargetUsage::Status::Private) {
                    deps_which_should_be_private.push_back(dep->name);
                }
            }
        }
        result.setDepsWhichShouldBePrivate(std::move(deps_which_should_be_private));
    }

    return result;
}

} // namespace dwyu
