load("//third_party:dependencies_step_1.bzl", "dependencies_step_1")

def setup_step_1():
    """
    Perform the initial setup steps for this project.

    We cannot execute load statements from external workspaces until they have been defined. Thus, we have to perform
    multiple iterations of loading a setup function and executing it from the WORKSPACE file.
    """
    dependencies_step_1()
