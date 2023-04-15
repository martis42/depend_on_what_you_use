workspace(name = "depend_on_what_you_use")

load("//:setup_step_1.bzl", "setup_step_1")

setup_step_1()

load("//:setup_step_2.bzl", "dev_setup_step_2", "setup_step_2")

setup_step_2()

dev_setup_step_2()

load("//:setup_step_3.bzl", "setup_step_3")

setup_step_3()

#
# Testing
#

load("//test/aspect:test.bzl", "test_setup")

test_setup()
