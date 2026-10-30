<!-- mdformat-toc start --slug=github --maxlevel=2 --minlevel=1 -->

- [Troubleshooting](#troubleshooting)
  - [Compiler errors](#compiler-errors)
  - [Target mapping fails due to mapping testonly targets](#target-mapping-fails-due-to-mapping-testonly-targets)

<!-- mdformat-toc end -->

# Troubleshooting<a name="troubleshooting"></a>

## Compiler errors<a name="compiler-errors"></a>

DWYU is developed with many active compiler warnings to make it unlikely that you see compiler warnings when using the DWYU tools with your C++ toolchain.
However, there are so many compiler warnings and compilers, that we can't guarantee this.

If you see compiler warnings related to DWYU or its transitive dependencies, you can silence them via [--per_file_copt](https://bazel.build/reference/command-line-reference#flag--per_file_copt) and [--host_per_file_copt](https://bazel.build/reference/command-line-reference#flag--host_per_file_copt).
For example if you see warnings coming from the `boost.wave` dependency, you could silence them like this in your `.bazelrc` file:

```bash
build --per_file_copt=boost.wave/src/.*@-w
build --host_per_file_copt=boost.wave/src/.*@-w
```

## Target mapping fails due to mapping testonly targets<a name="target-mapping-fails-due-to-mapping-testonly-targets"></a>

When Bazel applies an aspect to a target, it virtually treats the target under inspection like it depends on all the dependencies of the aspect.
This can become problematic when using a [target mapping](/docs/api/cc_info_mapping.md).

If you map `testonly = True` targets, then the `dwyu_make_cc_info_mapping` has to be marked testonly as well.
A DWYU aspect using such a testonly target mapping can no longer be applied to non testonly targets.

At the time of writing this, Bazel does not offer a flag to disable the testonly check.
You can however work around this problem:

- Create 2 target mappings, one including the mapping of the testonly targets, one without those.
- Create 2 DWYU aspects, one using only non testonly targets mapping and one using the mapping including the testonly targets.
- Execute DWYU 2 times on your stack:
  - Once on the non testonly targets with the aspect using the non testonly mappings.
  - Once on tests and testonly targets with the aspect using the mapping including the testonly targets.

Helpful tools for this:

- Query to get all testonly targets and tests (which implicitly set the testonly attribute): `bazel query 'attr(testonly, 1, //...)'`
- Query to get all non testonly targets: `bazel query 'kind(rule, //...) except attr(testonly, 1, //...)'`
- Use Bazel option [`--target_pattern_file`](https://bazel.build/reference/command-line-reference#param-target-pattern-file) to execute DWYU on a set of targets found via the queries and stored in a file.
  With Bazel >= 10 one can streamline this by using Bazel option [`--target-query`](https://bazel.build/reference/command-line-reference#param-target-query).
