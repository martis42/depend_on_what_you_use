#ifndef DWYU_ASPECT_PRIVATE_ANALYZE_INCLUDES_EVALUATE_INCLUDES_H
#define DWYU_ASPECT_PRIVATE_ANALYZE_INCLUDES_EVALUATE_INCLUDES_H

#include "dwyu/aspect/private/analyze_includes/include_statement.h"
#include "dwyu/aspect/private/analyze_includes/result.h"
#include "dwyu/aspect/private/analyze_includes/system_under_inspection.h"

#include <vector>

namespace dwyu {

Result evaluateIncludes(const std::vector<IncludeStatement>& public_includes,
                        const std::vector<IncludeStatement>& private_includes,
                        SystemUnderInspection& system_under_inspection,
                        const bool optimize_impl_deps);

} // namespace dwyu

#endif
