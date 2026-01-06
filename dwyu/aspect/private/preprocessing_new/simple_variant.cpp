#include "clang/AST/ASTConsumer.h"
#include "clang/Frontend/CompilerInstance.h"
#include "clang/Frontend/FrontendAction.h"
#include "clang/Frontend/FrontendActions.h"
#include "clang/Lex/PPCallbacks.h"
#include "clang/Lex/Preprocessor.h"
#include "clang/Tooling/CommonOptionsParser.h"
#include "clang/Tooling/Tooling.h"
#include "llvm/Support/CommandLine.h"
#include "llvm/Support/raw_ostream.h"

using namespace clang;
using namespace clang::tooling;

// Callback class that records all #include directives.
class IncludeCollector : public PPCallbacks {
  public:
    explicit IncludeCollector(Preprocessor& PP) : PP(PP) {}

    // This is called for each #include / #include_next / #import
    void InclusionDirective(SourceLocation HashLoc,
                            const Token& IncludeToken,
                            StringRef FileName,
                            bool IsAngled,
                            CharSourceRange FilenameRange,
                            OptionalFileEntryRef File,
                            StringRef SearchPath,
                            StringRef RelativePath,
                            const Module* Imported,
                            SrcMgr::CharacteristicKind FileType) override {
        const SourceManager& SM = PP.getSourceManager();

        // Filter: only report includes that appear in the main file,
        // not those coming from headers, if desired.
        if (!SM.isWrittenInMainFile(HashLoc))
            return;

        llvm::outs() << "include " << (IsAngled ? '<' : '"') << FileName << (IsAngled ? '>' : '"') << " at "
                     << HashLoc.printToString(SM) << "\n";
    }

  private:
    Preprocessor& PP;
};

// ASTConsumer that installs the PPCallbacks when the source file starts.
class IncludeConsumer : public ASTConsumer {
  public:
    explicit IncludeConsumer(CompilerInstance& CI) : CI(CI) {}

    void Initialize(ASTContext& Context) override {
        Preprocessor& PP = CI.getPreprocessor();
        PP.addPPCallbacks(std::make_unique<IncludeCollector>(PP));
    }

  private:
    CompilerInstance& CI;
};

class IncludeAction : public ASTFrontendAction {
  public:
    std::unique_ptr<ASTConsumer> CreateASTConsumer(CompilerInstance& CI, StringRef InFile) override {
        return std::make_unique<IncludeConsumer>(CI);
    }
};

static llvm::cl::OptionCategory FindIncludesCategory("find-includes options");

int main(int argc, const char** argv) {
    auto ExpectedParser = CommonOptionsParser::create(argc, argv, FindIncludesCategory);
    if (!ExpectedParser) {
        llvm::errs() << ExpectedParser.takeError();
        return 1;
    }
    CommonOptionsParser& OptionsParser = ExpectedParser.get();

    ClangTool Tool(OptionsParser.getCompilations(), OptionsParser.getSourcePathList());

    return Tool.run(newFrontendActionFactory<IncludeAction>().get());
}

/*
Usage example

```bash clang++ FindIncludes.cpp `llvm
- config-- cxxflags-- ldflags-- system - libs-- libs all` - o find - includes./ find - includes file.cpp-- - std =
c++ 20
```

- `PPCallbacks::InclusionDirective` is the canonical hook for all include-like directives in the Clang
preprocessor.[2]
- Use `SourceManager::isWrittenInMainFile` (shown above) if you only want includes written in the main file and not
inside headers.[3]
- If you need system headers too, drop the `isWrittenInMainFile` check and log everything.

[1](https://stackoverflow.com/questions/27029313/whats-the-right-way-to-match-includes-or-defines-using-clangs-libtooling)
[2](https://github.com/pr0g/clang-experiments/blob/main/examples/clang-ast-notes.md)
[3](https://stackoverflow.com/questions/76060406/clang-libtooling-ppcallbacks-only-for-defines-in-main-source-file)
[4](https://kevinaboos.wordpress.com/2013/07/23/clang-tutorial-part-ii-libtooling-example/)
[5](https://clang.llvm.org/doxygen/classclang_1_1Preprocessor.html)
[6](https://github.com/llvm/llvm-project/blob/main/clang/include/clang/Lex/Preprocessor.h)
[7](https://git-ce.rwth-aachen.de/yussur.oraji_rwth/llvm-newpass/-/blob/b98dde666d07a188071ee00f9fac2eab41273e5c/clang/lib/Tooling/DependencyScanning/ModuleDepCollector.cpp)
[8](https://stackoverflow.com/questions/13881506/retrieve-information-about-pre-processor-directives)
[9](https://www.kdab.com/cpp-with-clang-libtooling/)
[10](https://clang.llvm.org/docs/ClangCommandLineReference.html)
*/