Example of a source-modifying aspect, which applies the fixes for the findings of a DWYU aspect to the BUILD files.

This workspace is a standalone Bazel module.
Building `//...` with the fix aspect edits the BUILD files of this workspace and leaves the other examples unchanged.

The [fix aspect](dwyu_fix/fix_aspect.bzl) requires a DWYU aspect and propagates along `deps`.
For each target, it collects the headers of the dependency closure and the target owning each header.
A fix action per target reads the DWYU report of the target and the collected header owners.
The [fix tool](dwyu_fix/fix_deps.py) then removes unused dependencies and adds the owners of headers included without a direct dependency, using buildozer.

The fix action edits files in the source tree.
It runs locally and outside the sandbox, and it is not hermetic.
Parallel fix actions for targets of the same package serialize their edits through a lock on the package directory.

For brevity, the example ignores `implementation_deps`.

The [demo](demo/BUILD) package contains a target missing a direct dependency and a target with an unused dependency:

```shell
bazel build --config=dwyu //...
```

Applying the fixes edits [demo/BUILD](demo/BUILD):

```shell
bazel build --config=dwyu-fix //...
git diff demo/BUILD
```

Afterwards, DWYU reports no findings:

```shell
bazel build --config=dwyu //...
```

Bazel caches the fix action.
Reverting the BUILD file changes the DWYU report, which makes Bazel run the fix action again.
