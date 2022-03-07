load("//:defs.bzl", "dwyu_aspect_factory")

utilization_aspect = dwyu_aspect_factory(min_utilization = 50)
