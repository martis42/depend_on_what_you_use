import json
import os
import re
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

# // clang-format off
# po::options_description options("Allowed options");
# options.add_options()("help",
#                       "Produce help message");
# options.add_options()("file_under_inspection",
#                       po::value<std::string>(),
#                       "Source file we are analyzing");
# options.add_options()("preprocessor_output",
#                       po::value<std::string>(),
#                       "Preprocessor output listing all included header files");
# options.add_options()("output",
#                       po::value<std::string>(),
#                       "Json file containing the detected included header files");
# // clang-format on


def cli() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument(
        "--file_under_inspection",
        type=str,
        help="TBD",
    )
    parser.add_argument(
        "--preprocessor_output",
        metavar="FILE",
        type=Path,
        help="TBD",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        type=Path,
        help="TBD",
    )
    return parser.parse_args()


# def impl():


def rel_path(p: str):
    if str(p).startswith("/"):
        return p

    cwd = Path(os.getcwd())
    tmp = cwd / p
    tmp = tmp.resolve()
    return str(tmp.relative_to(cwd))


def main(args: Namespace) -> int:
    """
    Preprocessor output doc https://gcc.gnu.org/onlinedocs/cpp/Preprocessor-Output.html
    """
    includes = []

    with args.preprocessor_output.open(mode="rt", encoding="utf-8") as input:
        first_line = input.readline().strip()
        file_under_inspection = first_line.split("# 0 ")[1]
        file_under_inspection_marker = f"{file_under_inspection} 2"

        # print(f"DBG_1 '{first_line}'")
        # print(f"DBG_2 '{file_under_inspection}'")
        # print(f"DBG_3 '{file_under_inspection_marker}'")

        # skip header part
        header_line = input.readline()
        while file_under_inspection not in header_line:
            header_line = input.readline()

        inside_included_content = False
        for line in input.readlines():
            # print(f"LINE '{line.strip()}'")

            if not line.startswith("#"):
                continue

            if inside_included_content and file_under_inspection_marker in line:
                # We reached the end of content placed by an include
                inside_included_content = False
                continue

            if not inside_included_content:
                # Is there a 'find first' function?
                matches = re.findall('"(.+)" 1', line)
                # print(matches)
                if len(matches) == 1:
                    # We descend into another section of code added trough an include
                    inside_included_content = True
                    includes.append(matches[0])
                    continue

                if len(matches) > 1:
                    raise RuntimeError("TBD")

    includes = [rel_path(inc) for inc in includes]
    includes = list(set(includes))

    result = {
        "file": args.file_under_inspection,
        "included_headers": includes,
    }

    print("========================")
    print(args.preprocessor_output.read_text())
    print("========================")
    print(result)
    print("========================")

    # print("----------")
    # import os
    # print(os.getcwd())
    # print(os.listdir("."))

    # target_dir = args.output.parent
    # print(f"TARGET_D '{target_dir}'")
    # target_dir.mkdir(parents=True, exist_ok=True)
    with args.output.open(mode="wt", encoding="utf-8") as output:
        # Only store unique appearances of includes
        json.dump(result, output)

    return 0


if __name__ == "__main__":
    import os

    print("XXXXX, ", os.getcwd())

    cli_args = cli()
    sys.exit(main(cli_args))

##
## Broken C++ impl
##


# Failed tests:
# - 'ignore_includes/custom_ignore_include_paths' for Bazel 8.3.1 and Python 3.12
# - 'ignore_includes/extra_ignore_include_paths' for Bazel 8.3.1 and Python 3.12
# - 'ignore_includes/ignore_include_patterns' for Bazel 8.3.1 and Python 3.12
# - 'ignore_includes/include_not_covered_by_patterns' for Bazel 8.3.1 and Python 3.12
# - 'ignore_toolchain_headers/custom_toolchain_headers_info' for Bazel 8.3.1 and Python 3.12
# - 'tree_artifact/invalid_tree_artifact' for Bazel 8.3.1 and Python 3.12
# - 'using_transitive_dep/detect_using_transitive_dep' for Bazel 8.3.1 and Python 3.12
# - 'using_transitive_dep/detect_using_transitive_impl_dep' for Bazel 8.3.1 and Python 3.12


###
### Hacky Python impl
###

# Failed tests:
# - 'ignore_includes/custom_ignore_include_paths' for Bazel 8.3.1 and Python 3.12
# - 'ignore_includes/extra_ignore_include_paths' for Bazel 8.3.1 and Python 3.12
# - 'ignore_includes/ignore_include_patterns' for Bazel 8.3.1 and Python 3.12
# - 'ignore_includes/include_not_covered_by_patterns' for Bazel 8.3.1 and Python 3.12
# - 'ignore_toolchain_headers/custom_toolchain_headers_info' for Bazel 8.3.1 and Python 3.12
# - 'tree_artifact/invalid_tree_artifact' for Bazel 8.3.1 and Python 3.12
# - 'using_transitive_dep/detect_using_transitive_dep' for Bazel 8.3.1 and Python 3.12
# - 'using_transitive_dep/detect_using_transitive_impl_dep' for Bazel 8.3.1 and Python 3.12


##########################################

# https://github.com/john-blackburn/preprocessor

# All GCC default defines:
# touch foo.h; cpp -dM foo.h


# !!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!


# New concept:
# 1) Introduce C++ impl for processing deps for TreeArtifacts for low impact introduction of C++ based tools.
# 2) Use 'gcc -x c++ -E -std=c++20 -dM -DFOO=42 foo.h > defs2.txt' like cmd to get all default defines , or maybe even simply all defines per target to be able to properly do custom preprocessing
# 3) Use C++ impl based on https://github.com/john-blackburn/preprocessor, which has a "anal<ze includes only" mode, which is perfect for us


# !!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!


########

# cpplib (GNU C Preprocessor Library):

# The GNU C preprocessor (cpp), which handles macros, includes, and conditionals, is implemented as a reusable library called cpplib. This library can be embedded into other tools and provides access to the token stream as processed by the preprocessor. However, the public API is not especially stable, and it is aimed more at compiler and language toolchain integration rather than user-friendly standalone usage.
# https://github.com/gcc-mirror/gcc/blob/master/libcpp/include/line-map.h

# SuperC:

# SuperC is an open-source tool that can parse C code, preserving and understanding arbitrary usage of preprocessor directives (like #ifdefs and macros). It lexes and preprocesses code while retaining conditional branches, then builds an Abstract Syntax Tree (AST) representing this structure. The source code is in Java, not C/C++, but demonstrates a robust approach for "preprocessor-aware" parsing.

# PCp3:

# PCp3 is a framework and tool that integrates the GNU cpplib for preprocessing and a parser for C, allowing analysis of code that retains preprocessor information. It can trigger user-defined callbacks on both parsing and preprocessing actions. The core is in C with Perl scripting for extensibility, and it offers a basis for building preprocessor-aware code analysis.

# Yacfe:

# Yacfe is a parser designed to handle C/C++ source files "as is," using heuristics and grammar extensions to manage common preprocessor usage, without requiring a preprocessing step. It is not a traditional C/C++ library but is designed to enable more style-preserving code transformation and analysis.

# Tree-sitter:

# Tree-sitter is a modern incremental parsing library that can parse C and C++ code. However, it does not natively process preprocessor directives in the same way as cpp; instead, it usually expects preprocessed code or requires careful integration with preprocessor outputs. It excels at AST generation for C and C++ grammar, but integrating full preprocessor awareness is challenging.

# GNU Bison/Flex + cpplib:

# Some custom solutions embed the GNU cpplib preprocessing library (from GCC) and pair it with parsing frameworks like Flex/Bison to provide preprocessor-aware parsing in C or C++. The combination is not a single out-of-the-box library but represents standard practice for writing such tools.

# Other Related Solutions:

# Some tools, like Clang/LLVM, offer libclang or similar APIs that expose token streams and can report preprocessor events, although their usage can be heavyweight for simple preprocessing needs.

# Preprocessing is usually a distinct phase and not deeply integrated into most C/C++ syntax parsers, owing to the complexity and grammar ambiguity introduced by the preprocessor.

# Summary:

# If you are looking for a C or C++ library, your primary candidate is cpplib from GCC, possibly combined with Flex/Bison for full-language parsing.

# For language-agnostic or advanced parsing, tools like Tree-sitter (in C) and SuperC (in Java) provide solutions, with the former focused on incremental ASTs and the latter on preprocessor-aware parsing.

# There is no single library that fully integrates C/C++ parsing with preprocessor handling in an easy-to-use C/C++ API (as most tools are highly customized), but the above solutions represent the best current state.
