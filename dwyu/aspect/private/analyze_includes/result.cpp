#include "dwyu/aspect/private/analyze_includes/result.h"

#include <nlohmann/json.hpp>

#include <fstream>
#include <string>
#include <vector>

using json = nlohmann::json;

namespace dwyu {
namespace {

std::map<std::string, std::vector<std::string>> makeMissingIncludesMap(const std::vector<IncludeStatement>& includes) {
    std::map<std::string, std::vector<std::string>> map{};
    for (const auto& inc : includes) {
        const auto it_file = map.find(inc.file);
        if (it_file == map.end()) {
            map.insert({inc.file, {inc.include}});
        }
        else {
            it_file->second.push_back(inc.include);
        }
    }
    return map;
}

} // namespace

Result::Result(const std::string& target, bool optimize_impl_deps)
    : target_{target}, optimize_impl_deps_{optimize_impl_deps} {}

bool Result::isOk() const {
    return public_includes_without_direct_dep_.empty() && private_includes_without_direct_dep_.empty() &&
           unused_deps_.empty() && unused_impl_deps_.empty() && public_dep_which_should_be_private_.empty();
}

void Result::setPublicIncludesWithoutDirectDep(std::vector<IncludeStatement> includes) {
    public_includes_without_direct_dep_ = std::move(includes);
}

void Result::Result::setPrivateIncludesWithoutDirectDep(std::vector<IncludeStatement> includes) {
    private_includes_without_direct_dep_ = std::move(includes);
}

void Result::setUnusedDeps(std::vector<std::string> deps) {
    unused_deps_ = std::move(deps);
}

void Result::setUnusedImplDeps(std::vector<std::string> deps) {
    unused_impl_deps_ = std::move(deps);
}

void Result::setDepsWhichShouldBePrivate(std::vector<std::string> deps) {
    public_dep_which_should_be_private_ = std::move(deps);
}

std::string Result::toString() const {
    const std::string frame{"================================================================================\n"};

    std::string content{"DWYU analyzing: " + target_ + "\n\n"};
    if (isOk()) {
        content += "Result: SUCCESS\n";
        return frame + content + frame;
    }

    content += "Result: FAILURE\n";

    if (!public_includes_without_direct_dep_.empty() || !private_includes_without_direct_dep_.empty()) {
        content += "\nIncludes which are not available from the direct dependencies:\n";
        for (const auto& include : public_includes_without_direct_dep_) {
            content += "  In file '" + include.file + "' include: " + include.include + "\n";
        }
        for (const auto& include : private_includes_without_direct_dep_) {
            content += "  In file '" + include.file + "' include: " + include.include + "\n";
        }
    }

    if (!unused_deps_.empty()) {
        content += "\nUnused dependencies in 'deps' (none of their headers are included):\n";
        for (const auto& dep : unused_deps_) {
            content += "  " + dep + "\n";
        }
    }

    if (!unused_impl_deps_.empty()) {
        content += "\nUnused dependencies in 'implementation_deps' (none of their headers are included):\n";
        for (const auto& dep : unused_impl_deps_) {
            content += "  " + dep + "\n";
        }
    }

    if (!public_dep_which_should_be_private_.empty()) {
        content +=
            "\nDependencies in 'deps' used only in private code which should be moved to 'implementation_deps':\n";
        for (const auto& dep : public_dep_which_should_be_private_) {
            content += "  " + dep + "\n";
        }
    }

    return frame + content + frame;
}

nlohmann::json Result::toJson() const {
    json data{};
    data["analyzed_target"] = target_;
    data["public_includes_without_dep"] = makeMissingIncludesMap(public_includes_without_direct_dep_);
    data["private_includes_without_dep"] = makeMissingIncludesMap(private_includes_without_direct_dep_);
    data["unused_deps"] = unused_deps_;
    data["unused_implementation_deps"] = unused_impl_deps_;
    data["deps_which_should_be_private"] = public_dep_which_should_be_private_;
    data["use_implementation_deps"] = optimize_impl_deps_;
    return data;
}

} // namespace dwyu
