#ifndef DWYU_CC_ASPECT_PRIVATE_PREPROCESSING_WAVE_PREPROCESSING_HOOK_BASE_H
#define DWYU_CC_ASPECT_PRIVATE_PREPROCESSING_WAVE_PREPROCESSING_HOOK_BASE_H

#include <boost/wave/cpp_exceptions.hpp>
#include <boost/wave/preprocessing_hooks.hpp>

#include <string>
#include <tuple>

namespace dwyu {

// Base class with behavior common to all our preprocessing modi
struct PreprocessingHooksBase : public boost::wave::context_policies::default_preprocessing_hooks {
    // 'state_corrupted' is set to true when we swallow an exception after which the boost::wave state can no longer
    // be trusted. The conditional and include bookkeeping might be broken, causing include statements to be silently
    // dropped. The caller owns the flag and can use it to process the affected file with a different strategy.
    explicit PreprocessingHooksBase(bool& state_corrupted) : state_corrupted_{state_corrupted} {}

    // Swallowing an error is expected to corrupt the preprocessor state. The exception is 'bad_include_file', which
    // is raised for each header which cannot be found. This is the norm for us, since DWYU deliberately does not
    // provide the CC toolchain headers to the preprocessing.
    static bool is_benign_swallow(const boost::wave::preprocess_exception& exception) {
        return exception.get_errorcode() == boost::wave::preprocess_exception::bad_include_file;
    }

    template <typename ExceptionT>
    static bool is_benign_swallow(const ExceptionT& exception) {
        std::ignore = exception;
        return false;
    }

    // Swallowing a warning is normally harmless. However, boost::wave raises these two warnings while giving up on
    // expanding a macro invoked with too few arguments (e.g. a variadic macro invoked without variadic arguments,
    // which is valid since C++20). boost::wave then reports the end of the input and thus silently stops preprocessing
    // the remainder of the file.
    static bool aborts_preprocessing(const boost::wave::preprocess_exception& exception) {
        return exception.get_errorcode() == boost::wave::preprocess_exception::too_few_macroarguments ||
               exception.get_errorcode() == boost::wave::preprocess_exception::empty_macroarguments;
    }

    template <typename ExceptionT>
    static bool aborts_preprocessing(const ExceptionT& exception) {
        std::ignore = exception;
        return false;
    }

    template <typename ContextT, typename ContainerT>
    bool found_warning_directive(ContextT const& ctx, ContainerT const& message) {
        std::ignore = ctx;
        std::ignore = message;

        // We don't care about warning directives, aka '#warning "Some msg"'
        return true;
    }

    template <typename ContextT, typename ContainerT>
    bool found_error_directive(ContextT const& ctx, ContainerT const& message) {
        std::ignore = ctx;
        std::ignore = message;

        // We don't care about error directives, aka '#error "Some msg"'
        //
        // !! This means we might evaluate invalid code paths while preprocessing !!
        //
        // This is not as bad as it sounds. One of our Assumptions of Use is that we analyze valid and compiling code.
        // Thus, we know the code is fine and if we hit an error it is due to us using a wrong configuration.
        //
        // We can't guarantee to know the correct configuration. There are a lot of macros defining how the
        // platform works and what system libraries features are available. Those are mostly not provided via the
        // command line, but determined by the CC toolchain preprocessor and compiler internally. We don't have access
        // to those in DWYU. Various experiments on our side have shown that trying to behave exactly as the compiler
        // is futile or at least requrires an amount of work this hobby project cannot invest.
        //
        // Not ignoring errors would be inconsistent. We, also skip the CC toolchain standard library and system
        // headers during preprocessing because of the problem described above.
        //
        // We consider the impact of this design flaw as low. We are not trying to compile the code. We only preprocess
        // it to find all relevant include statements for the active build configuration. As far as we can tell the
        // likelihood of a conditional include statement in the user's code being based on such a low level compiler
        // internal macro is low. Most conditional include statements are based on macros injected via Bazel to
        // accommodate variation points in the build system. We can handle those without problem, since they are known
        // to Bazel and thus also to us.
        return true;
    }

    template <typename ContextT, typename ExceptionT>
    void throw_exception(const ContextT& ctx, const ExceptionT& exception) {
        // We ignore most exceptions, but remember if doing so corrupted the preprocessor state.
        const auto severity = exception.get_severity();
        if (severity == boost::wave::util::severity::severity_remark ||
            severity == boost::wave::util::severity::severity_warning) {
            // Remarks and warnings are either way not relevant for us
            if (aborts_preprocessing(exception)) {
                state_corrupted_ = true;
            }
            return;
        }
        if (severity == boost::wave::util::severity::severity_error) {
            // Even errors have to be ignored because they can easily appear due to parsing code with a wrong
            // configuration. For a detailed explanation see the comment in the 'found_error_directive' callback.
            if (!is_benign_swallow(exception)) {
                state_corrupted_ = true;
            }
            return;
        }
        boost::wave::context_policies::default_preprocessing_hooks::throw_exception(ctx, exception);
    }

  private:
    // NOLINTNEXTLINE(cppcoreguidelines-avoid-const-or-ref-data-members) By design to make the value available to caller
    bool& state_corrupted_;
};

} // namespace dwyu

#endif
