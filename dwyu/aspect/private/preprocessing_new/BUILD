load("@rules_cc//cc:cc_binary.bzl", "cc_binary")

cc_binary(
    name = "main",
    srcs = ["clang_include_extractor.cpp"],
    deps = [
        "@llvm-project//clang:frontend",
        "@llvm-project//clang:lex",
    ],
)
