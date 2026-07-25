Demonstrate how one can modify the DWYU behavior for individual targets by overwriting the DWYU aspect settings via tags.

Under normal circumstances, the demonstration targets would fail the DWYU analysis.
We configure them with tags to not fail the DWYU analysis performed on this package.

Execute the following to see that the DWYU analysis is green, despite the various issues if the targets (see comments int he `BUILD` file).

```shell
bazel build --config=dwyu //configuration_via_tags/...
```

Please note, this technique is intended to specify individual exceptions.
If you want to change the DWYU behavior globally, do s via the aspect factory parameters.
