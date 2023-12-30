You might want to execute DWYU automatically as part of your build and test cycle without having to execute DWYU every time explicitly as extra step.
One possibility to do so is by adding

```
build --aspects=//:aspect.bzl%dwyu # exemplary aspect file and aspect name
build --output_groups=dwyu
```

to your `bazelrc` file.
Then, DWYU is automatically executed in parallel to each build command.
This is however a bad solution if you want to execute DWYU only on a sub set of targets automatically.

To achieve DWYU execution as part of a build command for a specific set of targets you can create a custom rule to do so.
Writing such a rule is trivial, as demonstrated in [rule.bzl](./rule.bzl).

Executing <br>
`bazel build //rule_using_dwyu/...` <br>
fails due to DWYU automatically being executed and analyzing the fauly target.
