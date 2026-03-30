import json
import logging
from dataclasses import dataclass
from itertools import chain

from dwyu.apply_fixes.bazel_query import BazelQuery

log = logging.getLogger()


@dataclass
class Dependency:
    target: str
    # Assuming no include path manipulation, the target provides these headers
    headers: list[str]

    def __repr__(self) -> str:
        return f"Dependency(target={self.target}, headers={self.headers})"


def target_to_path(dep: str) -> str:
    return dep.replace(":", "/").rsplit("//", 1)[1]


def get_string_attribute(attrs: list[dict[str, str]], attribute: str) -> str:
    """
    Work on the list of attributes of a target as it is returned by a Bazel query
    """
    for attr in attrs:
        if attr["name"] == attribute and attr["explicitlySpecified"] and "stringValue" in attr:
            return attr["stringValue"]
    return ""


def starlark_hash_as_hex_string(string: str) -> str:
    """
    Starlark hash function: https://bazel.build/rules/lib/globals/all#hash
    We don't need the integer value, but want the behavior of:
    "%x" % hash(42)
    """
    hash_value = 0
    # Java hashes UTF-16 code units, not Unicode code points
    utf16 = string.encode("utf-16-be")
    for i in range(0, len(utf16), 2):
        code_unit = (utf16[i] << 8) | utf16[i + 1]
        hash_value = (31 * hash_value + code_unit) & 0xFFFFFFFF  # wrap to 32-bit

    return f"{hash_value:x}"


def virtualize_headers(
    header_labels: list[str], target_name: str, added_prefix: str, stripped_prefix: str
) -> list[str]:
    """
    cc_library targets using 'include_prefix' and/or 'strip_include_prefix' create new header files in a virtual
    location. The preprocessor will discover these virtual header files instead of the real header files provided
    by the dependency. Thus, our comparison of included files of the target under inspection and the header files
    specified by dependencies won't match. To enable matching, we recreate the virtual header file paths here.

    In reality these header will be below the '/bin/' directory for generated code. However, since we either way ignore
    the path before '/bin/' in the analysis, we skip this here.
    A typical real virtual header file path looks like:
    bazel-out/k8-fastbuild/bin/<path_to_pkg>/_virtual_includes/<target_name>/<prefix>/<file_name_minus_stripped_part>

    There can be another version of the virtual header file. When toolchain feature 'shorten_virtual_includes' is used
    (e.g. with rules_cc >= 0.1.3 automatically on Windows), the file path is:
    bazel-out/k8-fastbuild/bin/_virtual_includes/<hash_for_pkg_path_and_target_name>/<prefix>/<file_name_minus_stripped_part>
    """
    hdrs = []
    for label in header_labels:
        pkg, file = label.rsplit(":", maxsplit=1)
        pkg = pkg.rsplit("//", maxsplit=1)[1]

        # If the target s from the root package, we don't want a leading '/' due to the empty package path
        pkg_part = "" if pkg == "" else f"{pkg}/"

        # Prefixing and stripping logic works on the file path relative to the cc_library target
        file = file.split(f"{stripped_prefix}/", maxsplit=1)[1] if stripped_prefix else file
        prefix = f"{added_prefix}/" if added_prefix else ""
        include_root_hash = starlark_hash_as_hex_string(pkg + "/" + target_name)

        hdrs.append(f"{pkg_part}_virtual_includes/{target_name}/{prefix}{file}")
        hdrs.append(f"_virtual_includes/{include_root_hash}/{prefix}{file}")
    return hdrs


def get_dependencies(bazel_query: BazelQuery, target: str) -> list[Dependency]:
    """
    Extract dependencies from a given target together with further information about those dependencies.
    """

    # We ignore implementation_deps as they are only able to provide headers to the target under inspection as
    # direct dependency. We are searching for transitive dependencies providing headers to the target under inspection.
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
                    # One can always use the raw header paths, thus unconditionally evaluate them
                    hdrs = [target_to_path(hdr) for hdr in attr["stringListValue"]]

                    added_prefix = get_string_attribute(x["rule"]["attribute"], "include_prefix")
                    stripped_prefix = get_string_attribute(x["rule"]["attribute"], "strip_include_prefix")
                    if added_prefix or stripped_prefix:
                        virtual_hdrs = virtualize_headers(
                            header_labels=attr["stringListValue"],
                            target_name=get_string_attribute(x["rule"]["attribute"], "name"),
                            added_prefix=added_prefix,
                            stripped_prefix=stripped_prefix,
                        )
                        hdrs.extend(virtual_hdrs)
                    deps.append(Dependency(target=x["rule"]["name"], headers=hdrs))
                    break

    return deps


def is_visible(bazel_query: BazelQuery, target: str, dep: str) -> bool:
    """
    We can find dependencies, which are actually not usable. For example, the cc_library providing the required
    header file might be private and only some alias target pointing to it might be visible for the target
    consuming the header file.
    """
    process = bazel_query.execute(query=f"visible({target}, {dep})", args=[], enforce_query=True)
    return process.stdout != ""


def is_matching_header(desired_header: str, provided_header: str) -> bool:
    """
    If the desired header is generated code, it has a path similar to 'bazel-out/k8-fastbuild/bin/foo/bar.h', but the
    target providing it reports 'foo/bar.h'
    If the desired header is from external code, it has a path similar to 'external/some_repo/foo/bar.h', but the
    target providing it reports 'foo/bar.h'
    """
    if "/bin/" in desired_header:
        desired_header = desired_header.split("/bin/", maxsplit=1)[1]
    if desired_header.startswith("external/"):
        desired_header = desired_header.split("/", maxsplit=2)[2]
    return desired_header == provided_header


def match_deps_to_header(
    bazel_query: BazelQuery, target: str, header: str, target_deps: list[Dependency]
) -> str | None:
    """
    From the preprocessing step we know the whole path of the desired header file in the Bazel sandbox structure.
    We can simply compare the sandbox paths of the header files provided by the dependencies with the path of the
    invalid include to find a matching dependency.
    """

    deps_providing_header = [
        dep.target
        for dep in target_deps
        if any(is_matching_header(desired_header=header, provided_header=hdr) for hdr in dep.headers)
    ]
    visible_deps_providing_header = [
        dep for dep in deps_providing_header if is_visible(bazel_query=bazel_query, target=target, dep=dep)
    ]

    if len(visible_deps_providing_header) == 1:
        return visible_deps_providing_header[0]

    if len(visible_deps_providing_header) > 1:
        log.warning(
            f"""
Found multiple targets providing the header file '{header}' required by target '{target}'.
  Cannot determine correct dependency.
  Discovered potential dependencies are: {visible_deps_providing_header}.
            """.strip()
        )
        return None

    log.warning(
        f"""
Could not find a dependency providing providing the header file '{header}' for target '{target}'.
  Is the header file maybe wrongly part of the 'srcs' attribute instead of 'hdrs' in the library which should provide the header?
  Or is this include resolved through the toolchain instead of through a dependency?
        """.strip()
    )
    return None


def search_missing_deps(
    bazel_query: BazelQuery, target: str, headers_without_direct_dep: dict[str, list[str]]
) -> list[str]:
    """
    Search for targets providing header files matching the include statements in the transitive dependencies of the
    target under inspection.
    """
    if not headers_without_direct_dep:
        return []

    target_deps = get_dependencies(bazel_query=bazel_query, target=target)
    header_files_without_direct_dep = list(chain(*headers_without_direct_dep.values()))
    return [
        dep
        for header in header_files_without_direct_dep
        if (dep := match_deps_to_header(bazel_query=bazel_query, target=target, header=header, target_deps=target_deps))
        is not None
    ]
