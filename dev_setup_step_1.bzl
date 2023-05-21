load("//third_party:dev_dependencies_step_1.bzl", "dev_dependencies_step_1")

def dev_setup_step_1():
    """
    Perform the initial development setup steps for this project.

    We cannot execute load statements from external workspaces until they have been defined. Thus, we have to perform
    multiple iterations of loading a setup function and executing it from the WORKSPACE file.
    """
    dev_dependencies_step_1()
