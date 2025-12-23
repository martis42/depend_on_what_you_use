#include "dwyu/aspect/private/analyze_includes/system_under_inspection.h"

#include <nlohmann/json.hpp>

#include <fstream>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>

//
#include <iostream>

using json = nlohmann::json;

namespace dwyu {
namespace {

json readJsonFromFile(const std::string& path) {
    // TODO check existence of file
    std::ifstream file{path};
    return json::parse(file);
}

void updateHeadersToDepsMap(const std::string& header_file,
                            std::shared_ptr<CcDependency> cc_dep,
                            SystemUnderInspection::HeadersToDepsMap& hdrs_to_deps_map) {
    auto hdr_it = hdrs_to_deps_map.find(header_file);
    if (hdr_it == hdrs_to_deps_map.end()) {
        hdrs_to_deps_map.insert({header_file, {std::move(cc_dep)}});
    }
    else {
        hdr_it->second.push_back(std::move(cc_dep));
    }
}

CcTargetUnderInspection getTargetUnderInspectionFromFile(const std::string& file) {
    const auto data = readJsonFromFile(file);

    CcTargetUnderInspection target{};
    target.name = data["target"].get<std::string>();
    target.header_files = data["header_files"].get<std::unordered_set<std::string>>();

    return target;
}

} // namespace

void TargetUsage::update(Status usage_update) {
    if (usage_update == Status::None) {
        throw std::invalid_argument{"Resetting the usage to 'None' is not supported"};
    }

    if (usage_ == Status::PublicAndPrivate) {
        // The input cannot change anything
        return;
    }

    if (is_used() == false || usage_update == Status::PublicAndPrivate) {
        usage_ = usage_update;
    }
    else if ((usage_ == Status::Private && usage_update == Status::Public) ||
             (usage_ == Status::Public && usage_update == Status::Private)) {
        usage_ = Status::PublicAndPrivate;
    }
}

SystemUnderInspection getSystemUnderInspection(const std::string& target_under_inspection,
                                               const std::vector<std::string>& deps,
                                               const std::vector<std::string>& impl_deps) {
    SystemUnderInspection system{};

    system.target_under_inspection = getTargetUnderInspectionFromFile(target_under_inspection);

    for (const auto& file_path : deps) {
        const auto data = readJsonFromFile(file_path);
        auto cc_dep = std::make_shared<CcDependency>(CcDependency{data["target"].get<std::string>(), TargetUsage{}});
        for (const auto& header_file : data["header_files"].get<std::vector<std::string>>()) {
            updateHeadersToDepsMap(header_file, cc_dep, system.headers_to_public_deps_map);
            updateHeadersToDepsMap(header_file, cc_dep, system.headers_to_all_deps_map);
        }
    }

    for (const auto& file_path : impl_deps) {
        const auto data = readJsonFromFile(file_path);
        auto cc_dep = std::make_shared<CcDependency>(CcDependency{data["target"].get<std::string>(), TargetUsage{}});
        for (const auto& header_file : data["header_files"].get<std::vector<std::string>>()) {
            updateHeadersToDepsMap(header_file, cc_dep, system.headers_to_all_deps_map);
        }
    }

    return system;
}

} // namespace dwyu
