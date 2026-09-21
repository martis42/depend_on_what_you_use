#include "dwyu/cc/aspect/private/preprocessing/wave/preprocessing_hook_base.h"

#include <boost/wave/cpp_exceptions.hpp>
#include <boost/wave/cpplexer/cpplexer_exceptions.hpp>
#include <gtest/gtest.h>

namespace dwyu {
namespace {

// The context is only forwarded to the default hooks, which ignore it
struct DummyContext {};

boost::wave::preprocess_exception makePreprocessException(const boost::wave::preprocess_exception::error_code code) {
    return boost::wave::preprocess_exception{"some description", code, 1, 1, "some_file.h"};
}

boost::wave::cpplexer::lexing_exception
makeLexingException(const boost::wave::cpplexer::lexing_exception::error_code code) {
    return boost::wave::cpplexer::lexing_exception{"some description", code, 1, 1, "some_file.h"};
}

template <typename ExceptionT>
bool swallowingCorruptsState(const ExceptionT& exception) {
    bool state_corrupted{false};
    PreprocessingHooksBase hooks{state_corrupted};

    hooks.throw_exception(DummyContext{}, exception);

    return state_corrupted;
}

TEST(ThrowException, RemarksAreIgnored) {
    EXPECT_FALSE(
        swallowingCorruptsState(makePreprocessException(boost::wave::preprocess_exception::pragma_message_directive)));
}

TEST(ThrowException, WarningsAreIgnored) {
    EXPECT_FALSE(
        swallowingCorruptsState(makePreprocessException(boost::wave::preprocess_exception::macro_redefinition)));
    EXPECT_FALSE(
        swallowingCorruptsState(makePreprocessException(boost::wave::preprocess_exception::too_many_macroarguments)));
    EXPECT_FALSE(
        swallowingCorruptsState(makePreprocessException(boost::wave::preprocess_exception::unbalanced_if_endif)));
    EXPECT_FALSE(
        swallowingCorruptsState(makeLexingException(boost::wave::cpplexer::lexing_exception::generic_lexing_warning)));
}

TEST(ThrowException, WarningsAbortingThePreprocessingCorruptTheState) {
    // boost::wave raises those while giving up on expanding a macro and then stops processing the file
    EXPECT_TRUE(
        swallowingCorruptsState(makePreprocessException(boost::wave::preprocess_exception::too_few_macroarguments)));
    EXPECT_TRUE(
        swallowingCorruptsState(makePreprocessException(boost::wave::preprocess_exception::empty_macroarguments)));
}

TEST(ThrowException, MissingIncludeFileIsIgnored) {
    // Headers which cannot be found are expected, since DWYU deliberately does not provide the CC toolchain headers
    EXPECT_FALSE(swallowingCorruptsState(makePreprocessException(boost::wave::preprocess_exception::bad_include_file)));
}

TEST(ThrowException, ErrorsCorruptTheState) {
    EXPECT_TRUE(
        swallowingCorruptsState(makePreprocessException(boost::wave::preprocess_exception::ill_formed_expression)));
    EXPECT_TRUE(
        swallowingCorruptsState(makePreprocessException(boost::wave::preprocess_exception::missing_matching_endif)));
    EXPECT_TRUE(
        swallowingCorruptsState(makeLexingException(boost::wave::cpplexer::lexing_exception::generic_lexing_error)));
}

TEST(ThrowException, FatalExceptionsAreRethrown) {
    bool state_corrupted{false};
    PreprocessingHooksBase hooks{state_corrupted};
    const auto exception = makePreprocessException(boost::wave::preprocess_exception::include_nesting_too_deep);

    EXPECT_THROW(hooks.throw_exception(DummyContext{}, exception), boost::wave::preprocess_exception);
    EXPECT_FALSE(state_corrupted);
}

} // namespace
} // namespace dwyu
