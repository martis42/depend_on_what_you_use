// Standalone tool that uses Clang's preprocessor to list the headers
// directly included from a given C++ source file.
//
// Behavior:
//  - Only reports includes that originate from the main file (the file
//    passed on the command line), not from headers included by it.
//  - For each such include, prints the fully resolved filesystem path
//    of the header as determined by Clang's header search.
//  - If an included header cannot be resolved (missing header), it is
//    silently skipped.
//
// This tool assumes a standard LLVM/Clang installation is available.

#include "clang/Basic/Diagnostic.h"
#include "clang/Basic/DiagnosticOptions.h"
#include "clang/Basic/FileManager.h"
#include "clang/Basic/LangOptions.h"
#include "clang/Basic/SourceManager.h"
#include "clang/Basic/TargetInfo.h"
#include "clang/Basic/TargetOptions.h"
#include "clang/Frontend/CompilerInstance.h"
#include "clang/Frontend/FrontendOptions.h"
#include "clang/Frontend/LangStandard.h"
#include "clang/Frontend/Utils.h"
#include "clang/Lex/HeaderSearchOptions.h"
#include "clang/Lex/PPCallbacks.h"
#include "clang/Lex/Preprocessor.h"
#include "clang/Lex/PreprocessorOptions.h"
#include "clang/Lex/Token.h"

#include "llvm/ADT/IntrusiveRefCntPtr.h"
#include "llvm/ADT/StringRef.h"
#include "llvm/Support/CommandLine.h"
#include "llvm/Support/Host.h"
#include "llvm/Support/InitLLVM.h"
#include "llvm/Support/Path.h"
#include "llvm/Support/raw_ostream.h"

#include <memory>
#include <string>
#include <utility>
#include <vector>

using namespace clang;

namespace {

class IncludeCollectorCallbacks : public PPCallbacks {
  public:
    IncludeCollectorCallbacks(SourceManager& SM, std::vector<std::string>& Collected) : SM(SM), Collected(Collected) {}

    void InclusionDirective(SourceLocation HashLoc,
                            const Token& /*IncludeTok*/,
                            llvm::StringRef /*FileName*/,
                            bool /*IsAngled*/,
                            CharSourceRange /*FilenameRange*/,
                            const FileEntry* IncludedFile,
                            llvm::StringRef /*SearchPath*/,
                            llvm::StringRef /*RelativePath*/,
                            const Module* /*Imported*/,
                            SrcMgr::CharacteristicKind /*FileType*/) override {
        // Only consider includes coming from the main file.
        if (!SM.isInMainFile(HashLoc))
            return;

        // If the header could not be resolved, skip it.
        if (!IncludedFile)
            return;

        llvm::StringRef Name = IncludedFile->getName();
        if (!Name.empty())
            Collected.emplace_back(Name.str());
    }

  private:
    SourceManager& SM;
    std::vector<std::string>& Collected;
};

struct ParsedArgs {
    std::string InputFile;
    std::vector<std::string> IncludePaths;
    std::vector<std::string> MacroDefs;
};

// Very small argument parser:
//   clang_include_extractor [clang-like options...] <source-file>
// Supported options:
//   -I<path> or -I <path>
//   -D<name>[=value] or -D <name>[=value]
bool parseCommandLine(int argc, const char** argv, ParsedArgs& Out, llvm::raw_ostream& Errs) {
    if (argc < 2) {
        Errs << "Usage: " << argv[0] << " [-Ipath ...] [-Dmacro[=value] ...] <source-file>\n";
        return false;
    }

    std::vector<std::string> Args;
    Args.assign(argv + 1, argv + argc);

    std::string InputFile;
    for (size_t I = 0; I < Args.size(); ++I) {
        const std::string& A = Args[I];
        if (A == "-I") {
            if (I + 1 >= Args.size()) {
                Errs << "error: -I expects a directory\n";
                return false;
            }
            Out.IncludePaths.push_back(Args[++I]);
        }
        else if (A.rfind("-I", 0) == 0 && A.size() > 2) {
            Out.IncludePaths.push_back(A.substr(2));
        }
        else if (A == "-D") {
            if (I + 1 >= Args.size()) {
                Errs << "error: -D expects a macro definition\n";
                return false;
            }
            Out.MacroDefs.push_back(Args[++I]);
        }
        else if (A.rfind("-D", 0) == 0 && A.size() > 2) {
            Out.MacroDefs.push_back(A.substr(2));
        }
        else if (!A.empty() && A[0] == '-') {
            Errs << "warning: ignoring unsupported option '" << A << "'\n";
        }
        else {
            if (!InputFile.empty()) {
                Errs << "error: multiple input files specified: '" << InputFile << "' and '" << A << "'\n";
                return false;
            }
            InputFile = A;
        }
    }

    if (InputFile.empty()) {
        Errs << "error: no input file specified\n";
        return false;
    }

    Out.InputFile = std::move(InputFile);
    return true;
}

} // end anonymous namespace

int main(int argc, const char** argv) {
    llvm::InitLLVM X(argc, argv);

    ParsedArgs PArgs;
    if (!parseCommandLine(argc, argv, PArgs, llvm::errs()))
        return 1;

    CompilerInstance CI;

    // Diagnostics
    auto DiagOpts = std::make_shared<DiagnosticOptions>();
    auto DiagClient = new TextDiagnosticPrinter(llvm::errs(), &*DiagOpts, /*OwnsOutput=*/false);

    IntrusiveRefCntPtr<DiagnosticIDs> DiagID(new DiagnosticIDs());
    DiagnosticsEngine Diags(DiagID, &*DiagOpts, DiagClient);
    CI.setDiagnostics(&Diags);

    // Target
    auto TO = std::make_shared<TargetOptions>();
    TO->Triple = llvm::sys::getDefaultTargetTriple();
    TargetInfo* TI = TargetInfo::CreateTargetInfo(Diags, TO);
    CI.setTarget(TI);

    // File and source managers
    CI.createFileManager();
    CI.createSourceManager(CI.getFileManager());

    // Language options: treat input as C++17 by default.
    LangOptions& LangOpts = CI.getLangOpts();
    LangOpts.CPlusPlus = 1;
    LangOpts.CPlusPlus17 = 1;
    LangOpts.Bool = 1;

    // Header search paths from -I.
    HeaderSearchOptions& HSOpts = CI.getHeaderSearchOpts();
    for (const std::string& Inc : PArgs.IncludePaths) {
        HSOpts.AddPath(Inc, frontend::Angled, /*IsFramework=*/false,
                       /*IgnoreSysRoot=*/false);
    }

    // Preprocessor options.
    PreprocessorOptions& PPOpts = CI.getPreprocessorOpts();
    PPOpts.UsePredefines = true;
    for (const std::string& Macro : PArgs.MacroDefs) {
        PPOpts.addMacroDef(Macro);
    }

    // Create the preprocessor.
    CI.createPreprocessor(TU_Complete);

    // Find and set the main file.
    const FileEntry* MainFile = CI.getFileManager().getFile(PArgs.InputFile);
    if (!MainFile) {
        llvm::errs() << "error: cannot open input file '" << PArgs.InputFile << "'\n";
        return 1;
    }

    SourceManager& SM = CI.getSourceManager();
    FileID MainFileID = SM.createFileID(MainFile, SourceLocation(), SrcMgr::C_User);
    SM.setMainFileID(MainFileID);

    // Collect includes via callbacks.
    std::vector<std::string> CollectedIncludes;
    CI.getPreprocessor().addPPCallbacks(std::make_unique<IncludeCollectorCallbacks>(SM, CollectedIncludes));

    // Begin preprocessing the main source file.
    CI.getDiagnosticClient().BeginSourceFile(LangOpts, &CI.getPreprocessor());
    Preprocessor& PP = CI.getPreprocessor();
    PP.EnterMainSourceFile();

    Token Tok;
    bool HadError = false;
    while (true) {
        PP.Lex(Tok);
        if (Tok.is(tok::eof))
            break;
        if (Diags.hasFatalErrorOccurred()) {
            HadError = true;
            break;
        }
    }
    CI.getDiagnosticClient().EndSourceFile();

    if (HadError)
        return 1;

    // Print the collected, fully resolved include paths.
    for (const std::string& Path : CollectedIncludes) {
        llvm::outs() << Path << "\n";
    }

    return 0;
}
