from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from itertools import chain

from src.apply_fixes.bazel_query import BazelQuery

log = logging.getLogger()


@dataclass
class Dependency:
    target: str
    # Assuming no include path manipulation, the target provides these include paths
    include_paths: list[str]

    def __repr__(self) -> str:
        return f"Dependency(target={self.target}, include_paths={self.include_paths})"


def get_file_name(include: str) -> str:
    return include.split("/")[-1]


def target_to_path(dep: str) -> str:
    return dep.replace(":", "/").rsplit("//", 1)[1]


def get_dependencies(bazel_query: BazelQuery, target: str) -> list[Dependency]:
    """
    Extract dependencies from a given target together with further information about those dependencies.
    """
    output = "jsonproto" if bazel_query.uses_cquery else "streamed_jsonproto"
    process = bazel_query.execute(
        query=f'kind("rule", deps({target}) except deps({target}, 1))', args=[f"--output={output}", "--noimplicit_deps"]
    )

    if not process.stdout:
        # Targets without any dependency return nothing to stdout
        return []

    if bazel_query.uses_cquery:
        full_query = json.loads(process.stdout)
        queried_targets = [result["target"] for result in full_query["results"]]
    else:
        queried_targets = [json.loads(target) for target in process.stdout.strip().split("\n")]

    deps = []
    for x in queried_targets:
        if x["type"] == "RULE" and x["rule"]["ruleClass"].startswith("cc_"):
            for attr in x["rule"]["attribute"]:
                if attr["name"] == "hdrs" and attr["explicitlySpecified"] and "stringListValue" in attr:
                    deps.append(
                        Dependency(
                            target=x["rule"]["name"],
                            include_paths=[target_to_path(hdr) for hdr in attr["stringListValue"]],
                        )
                    )
                    break

    return deps


def match_deps_to_include(target: str, invalid_include: str, target_deps: list[Dependency]) -> str | None:
    """
    The possibility to manipulate include paths complicates matching potential dependencies to the invalid include
    statement. Thus, we perform this multistep heuristic.
    """

    deps_providing_included_path = [dep.target for dep in target_deps if invalid_include in dep.include_paths]

    if len(deps_providing_included_path) == 1:
        return deps_providing_included_path[0]

    if len(deps_providing_included_path) > 1:
        log.warning(
            f"""
Found multiple targets providing invalid include path '{invalid_include}' of target '{target}'.
 Cannot determine correct dependency.
 Discovered potential dependencies are: {deps_providing_included_path}.
            """.strip()
        )
        return None

    # No potential dep could be found searching for the full include statement. We perform a second search looking only
    # the file name of the invalid include. The file name cannot be altered by the various include path manipulation
    # techniques offered by Bazel, only the path at which a header can be discovered can be manipulated.
    included_file = get_file_name(invalid_include)
    deps_providing_included_file = [
        dep.target for dep in target_deps if included_file in [get_file_name(path) for path in dep.include_paths]
    ]

    if len(deps_providing_included_file) == 1:
        return deps_providing_included_file[0]

    if len(deps_providing_included_file) > 1:
        log.warning(
            f"""
Found multiple targets providing file '{included_file}' from invalid include '{invalid_include}' of target '{target}'.
 Matching the full include path did not work. Cannot determine correct dependency.
 Discovered potential dependencies are: {deps_providing_included_file}.
            """.strip()
        )
        return None

    log.warning(
        f"""
Could not find a proper dependency for invalid include path '{invalid_include}' of target '{target}'.
 Is the header file maybe wrongly part of the 'srcs' attribute instead of 'hdrs' in the library which should provide the header?
 Or is this include resolved through the toolchain instead of through a dependency?
        """.strip()
    )
    return None


def search_missing_deps(
    bazel_query: BazelQuery, target: str, includes_without_direct_dep: dict[str, list[str]]
) -> list[str]:
    """
    Search for targets providing header files matching the include statements in the transitive dependencies of the
    target under inspection.
    """
    if not includes_without_direct_dep:
        return []

    target_deps = get_dependencies(bazel_query=bazel_query, target=target)
    all_invalid_includes = list(chain(*includes_without_direct_dep.values()))
    return [
        dep
        for include in all_invalid_includes
        if (dep := match_deps_to_include(target=target, invalid_include=include, target_deps=target_deps)) is not None
    ]
