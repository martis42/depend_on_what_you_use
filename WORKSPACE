workspace(name = "depend_on_what_you_use")

#
# Setup of public dependencies of this project
#

load("//:setup_step_1.bzl", "setup_step_1")

setup_step_1()

load("//:setup_step_2.bzl", "setup_step_2")

setup_step_2()

#
# Setup of development dependencies of this project
#

load("//:dev_setup_step_1.bzl", "dev_setup_step_1")

dev_setup_step_1()

load("//:dev_setup_step_2.bzl", "dev_setup_step_2")

dev_setup_step_2()

load("//:dev_setup_step_3.bzl", "dev_setup_step_3")

dev_setup_step_3()

#
# Testing
#

load("//test/aspect:test.bzl", "test_setup")

test_setup()
