#include "dwyu/private/utils.h"

namespace dwyu {

std::string listToStr(const std::vector<std::string>& list) {
    std::string out{"["};
    for (const auto& element : list) {
        out += element + ", ";
    }
    if (out.size() > 1) {
        out.pop_back();
        out.back() = ']';
    }
    else {
        out += "]";
    }
    return out;
}

} // namespace dwyu
