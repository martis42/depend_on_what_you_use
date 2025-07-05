<!-- Generated with Stardoc: http://skydoc.bazel.build -->



<a id="dwyu_gather_cc_toolchain_headers"></a>

## dwyu_gather_cc_toolchain_headers

<pre>
load("@depend_on_what_you_use//src/toolchain_headers:toolchain_headers.bzl", "dwyu_gather_cc_toolchain_headers")

dwyu_gather_cc_toolchain_headers(<a href="#dwyu_gather_cc_toolchain_headers-name">name</a>)
</pre>

Analyze the active CC toolchain and extract include paths to header files which are available through the CC toolchain without any explicit dependency to a Bazel target.
Typically those are the standard library and system headers.

This rule analyzes [`CcToolchainInfo.built_in_include_directories`](https://bazel.build/rules/lib/providers/CcToolchainInfo#built_in_include_directories) and the toolchain compiler command line arguments to obtain this information.
We assume that all paths, which are not passed via the compiler command line with flags like `-isystem`, are specified via `CcToolchainInfo.built_in_include_directories`.
This includes also providing custom sysroots, which should be incorporated into `CcToolchainInfo.built_in_include_directories` according to the documentation of cc_common function [create_cc_toolchain_config_info](https://bazel.build/rules/lib/toplevel/cc_common#create_cc_toolchain_config_info).

**ATTRIBUTES**


| Name  | Description | Type | Mandatory | Default |
| :------------- | :------------- | :------------- | :------------- | :------------- |
| <a id="dwyu_gather_cc_toolchain_headers-name"></a>name |  A unique name for this target.   | <a href="https://bazel.build/concepts/labels#target-names">Name</a> | required |  |


