#include "dwyu/cc/aspect/private/preprocessing/wave/preprocessing_hook_base.h"

#include <boost/wave/cpp_exceptions.hpp>
#include <boost/wave/cpplexer/cpplexer_exceptions.hpp>
#include <gtest/gtest.h>

namespace dwyu {
namespace {

boost::wave::preprocess_exception makePreprocessException(const boost::wave::preprocess_exception::error_code code) {
    return boost::wave::preprocess_exception{"some description", code, 1, 1, "some_file.h"};
}

TEST(IsBenignSwallow, MissingIncludeFileIsBenign) {
    // Headers which cannot be found are expected, since DWYU deliberately does not provide the CC toolchain headers
    const auto exception = makePreprocessException(boost::wave::preprocess_exception::bad_include_file);

    EXPECT_TRUE(PreprocessingHooksBase::is_benign_swallow(exception));
}

TEST(IsBenignSwallow, OtherPreprocessingProblemsAreNotBenign) {
    const auto ill_formed_expression =
        makePreprocessException(boost::wave::preprocess_exception::ill_formed_expression);
    const auto too_few_macroarguments =
        makePreprocessException(boost::wave::preprocess_exception::too_few_macroarguments);
    const auto missing_matching_endif =
        makePreprocessException(boost::wave::preprocess_exception::missing_matching_endif);

    EXPECT_FALSE(PreprocessingHooksBase::is_benign_swallow(ill_formed_expression));
    EXPECT_FALSE(PreprocessingHooksBase::is_benign_swallow(too_few_macroarguments));
    EXPECT_FALSE(PreprocessingHooksBase::is_benign_swallow(missing_matching_endif));
}

TEST(IsBenignSwallow, LexingProblemsAreNotBenign) {
    const boost::wave::cpplexer::lexing_exception exception{
        "some description", boost::wave::cpplexer::lexing_exception::generic_lexing_error, 1, 1, "some_file.h"};

    EXPECT_FALSE(PreprocessingHooksBase::is_benign_swallow(exception));
}

} // namespace
} // namespace dwyu
