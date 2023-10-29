In some cases a user does not want to follow the DWYU design guidelines.
Maybe a public targets acts as proxy for implementation detail targets which are however providing the header files.
Or an external dependency is used which is assumed to be used in a specific way.

To prevent DWYU from raising errors in such cases, we allow mapping the headers provided by the dependencies of a target to the target itself.
