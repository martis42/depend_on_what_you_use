Bazel 6.0.0 introduces the experimental feature `interface_deps`, which can be activated through the flag `--experimental_cc_interface_deps`.
Doing so changes the meaning of the `cc_library` `deps` attribute from "all public and private dependencies" to "all private dependencies".
Include paths of private dependencies are not available to users of the `cc_library`.
The newly introduced attribute `interface_deps` defines all public depencies, which are available to users of the `cc_library`.

DWYU can scan the source code of a `cc_library` and raise an error for dependencies whose headers are solely used in private code (aka only listed in the `srcs` attribute) but are defined as `interface_deps`.
Such dependencies shall be moved to `deps` instead to prevent users of your library receiving more than they asked for and keeping dependency trees slim.
