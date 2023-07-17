A `TreeArtifact` is a special output of rules where one does not know beforehand how many output files will be generated.
Code generators are a common use case relying on this construct.
In other words, a `TreeArtifact` is a predeclared directory with unknown content.
The content will not be available until the execution phase.
Essentially, this makes it impossible to analyze a `TreeArtifact` in StarLark and requires doing so inside an action
which is performed in the execution phase.
