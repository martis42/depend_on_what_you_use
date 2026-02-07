#ifndef DWYU_ASPECT_PRIVATE_ANALYZE_INCLUDES_EVALUATE_INCLUDES_H
#define DWYU_ASPECT_PRIVATE_ANALYZE_INCLUDES_EVALUATE_INCLUDES_H

#include "dwyu/aspect/private/analyze_includes/include_statement.h"
#include "dwyu/aspect/private/analyze_includes/result.h"
#include "dwyu/aspect/private/analyze_includes/system_under_inspection.h"

#include <vector>

namespace dwyu {

// For the given include statements of the target under inspection, check which included header files are available
// through the direct dependencies.
// This function reports unused dependencies and invalid include statements. If 'optimize_impl_deps' is true, it also
// reports for 'cc_library' targets 'deps' which should be moved into 'implementation_deps'.
Result evaluateIncludes(const std::vector<IncludeStatement>& public_includes,
                        const std::vector<IncludeStatement>& private_includes,
                        SystemUnderInspection& system_under_inspection,
                        bool report_missing_direct_deps,
                        bool report_unused_deps,
                        bool optimize_impl_deps);

} // namespace dwyu

#endif
