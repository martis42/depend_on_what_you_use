You might want to execute DWYU automatically as part of your build and test cycle without having to execute DWYU every time explicitly as extra step.
One possibility to do so is by adding the following to your `bazelrc` file.

```
build --aspects=//:aspect.bzl%dwyu # exemplary aspect file and aspect name
build --output_groups=dwyu
```

Then, DWYU is automatically executed in parallel to each build command.
This is however a bad solution if you want to execute DWYU only on a sub set of targets automatically.

To achieve DWYU execution as part of a build command for a specific set of targets you can create a custom rule to do so.
Writing such a rule is trivial, as demonstrated in [rule.bzl](./rule.bzl).

Executing the following fails due to DWYU automatically being executed and analyzing the faulty target.

```shell
bazel build //rule_using_dwyu:dwyu
```

You need to be careful when using multiple DWYU based rules in parallel with various different aspects implementing them.
DWYU creates a report file for each target it analyzes.
If multiple rules invoke DWYU recursively based on different aspects, and they share common dependencies, there will be conflicts due to multiple actions creating the same file. <br>
This is not a problem if you have a single rule using one specific recursive DWYU aspect.
Bazel understands it has already executed aspect _X_ on a given target and will reuse the results instead of trying to execute it again.
Thus, no conflicting actions occur, no matter how many times you use the rule based on recursive aspect _X_ and how often transitive dependencies are visited.
