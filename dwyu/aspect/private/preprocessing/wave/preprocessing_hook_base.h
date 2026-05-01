#ifndef DWYU_ASPECT_PRIVATE_PREPROCESSING_WAVE_PREPROCESSING_HOOK_BASE_H
#define DWYU_ASPECT_PRIVATE_PREPROCESSING_WAVE_PREPROCESSING_HOOK_BASE_H

#include <boost/wave/cpp_exceptions.hpp>
#include <boost/wave/preprocessing_hooks.hpp>

#include <string>
#include <tuple>

namespace dwyu {

// Base class with behavior common to all our preprocessing modi
struct PreprocessingHooksBase : public boost::wave::context_policies::default_preprocessing_hooks {
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
        // We ignore most exceptions.
        // Remarks and warnings are either way not relevant for us
        // Even errors have to be ignored because they can easily appear due to parsing code with a wrong
        // configuration. For a detailed explanation see the comment in the 'found_error_directive' callback.
        if (exception.get_severity() == boost::wave::util::severity::severity_remark ||
            exception.get_severity() == boost::wave::util::severity::severity_warning ||
            exception.get_severity() == boost::wave::util::severity::severity_error) {
            return;
        }
        boost::wave::context_policies::default_preprocessing_hooks::throw_exception(ctx, exception);
    }
};

} // namespace dwyu

#endif
