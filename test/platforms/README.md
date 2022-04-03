This integration tests makes sure the DWYU aspect skips incompatible targets without raising an error.

Although `bazel build` is used to invoke an aspect and normally a build automatically skips incompatible targets, this is not the case for aspects.
An aspect is invoked an all targets matching the provided pattern no matter the compatibility.
Bazel does know though a target is incompatible.
The incompatible target has a `IncompatiblePlatformProvider` provider and is lacking `CcInfo`.
