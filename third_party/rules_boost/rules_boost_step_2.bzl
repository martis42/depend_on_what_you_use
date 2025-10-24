load("@com_github_nelhage_rules_boost//:boost/boost.bzl", "boost_deps")

def rules_boost_step_2():
    # Makes @boost available, e.g. '@boost//:algorithm'.
    boost_deps()
