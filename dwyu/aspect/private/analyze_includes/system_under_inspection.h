#ifndef DWYU_ASPECT_PRIVATE_ANALYZE_INCLUDES_SYSTEM_UNDER_INSPECTION_H
#define DWYU_ASPECT_PRIVATE_ANALYZE_INCLUDES_SYSTEM_UNDER_INSPECTION_H

#include <memory>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

namespace dwyu {

class TargetUsage {
  public:
    enum class Status {
        None,
        Public,
        Private,
        // TODO check if we really need this anymore. Can't public simply overrule private?
        PublicAndPrivate,
    };

    void update(Status usage_update);
    bool is_used() const { return usage_ != Status::None; }
    Status usage() const { return usage_; }

  private:
    Status usage_{Status::None};
};

struct CcTargetUnderInspection {
    std::string name;
    std::unordered_set<std::string> header_files;
};

struct CcDependency {
    std::string name;
    TargetUsage usage;
};

struct SystemUnderInspection {
    using HeadersToDepsMap = std::unordered_map<std::string, std::vector<std::shared_ptr<CcDependency>>>;

    CcTargetUnderInspection target_under_inspection;
    HeadersToDepsMap headers_to_public_deps_map;
    HeadersToDepsMap headers_to_all_deps_map;
};

SystemUnderInspection getSystemUnderInspection(const std::string& target_under_inspection,
                                               const std::vector<std::string>& deps,
                                               const std::vector<std::string>& impl_deps);

} // namespace dwyu

#endif
