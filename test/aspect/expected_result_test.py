from __future__ import annotations

import json
import unittest
from pathlib import Path

from expected_result import DWYU_FAILURE, DWYU_REPORT, ExpectedDwyuFailure, ExpectedFailure, ExpectedSuccess

from test.support.result import Error, Success


def make_failure(
    target: str = "//:foo:bar",
    invalid_includes: dict[str, list[str]] | None = None,
    unused_public_deps: list[str] | None = None,
    unused_private_deps: list[str] | None = None,
    deps_which_should_be_private: list[str] | None = None,
) -> ExpectedDwyuFailure:
    return ExpectedDwyuFailure(
        target=target,
        invalid_includes=invalid_includes if invalid_includes is not None else {},
        unused_public_deps=unused_public_deps if unused_public_deps is not None else [],
        unused_private_deps=unused_private_deps if unused_private_deps is not None else [],
        deps_which_should_be_private=deps_which_should_be_private if deps_which_should_be_private is not None else [],
    )


def make_report_data(
    analyzed_target: str = "//:foo:bar",
    invalid_pub_includes: dict[str, list[str]] | None = None,
    invalid_priv_includes: dict[str, list[str]] | None = None,
    unused_deps: list[str] | None = None,
    unused_impl_deps: list[str] | None = None,
    deps_which_should_be_private: list[str] | None = None,
) -> dict:
    return {
        "analyzed_target": analyzed_target,
        "public_includes_without_dep": invalid_pub_includes if invalid_pub_includes is not None else {},
        "private_includes_without_dep": invalid_priv_includes if invalid_priv_includes is not None else {},
        "unused_deps": unused_deps if unused_deps is not None else [],
        "unused_implementation_deps": unused_impl_deps if unused_impl_deps is not None else [],
        "deps_which_should_be_private": deps_which_should_be_private
        if deps_which_should_be_private is not None
        else [],
    }


class ExpectedDwyuFailureTest(unittest.TestCase):
    def test_check_expectation_for_no_expected_error(self) -> None:
        unit = make_failure()
        self.assertTrue(unit.check_expectation(make_report_data()))

    def test_check_expectation_for_expected_invalid_includes(self) -> None:
        unit = make_failure(
            invalid_includes={
                "priv.cpp": ["priv/some/header.h", "priv/other/header.h"],
                "pub.h": ["pub/some/header.h", "pub/other/header.h"],
            }
        )
        self.assertTrue(
            unit.check_expectation(
                make_report_data(
                    invalid_pub_includes={"pub.h": ["pub/other/header.h", "pub/some/header.h"]},
                    invalid_priv_includes={"priv.cpp": ["priv/other/header.h", "priv/some/header.h"]},
                )
            )
        )

    def test_check_expectation_for_unexpected_invalid_includes_src_file(self) -> None:
        unit = make_failure(invalid_includes={"foo.h": ["some/header.h"]})
        self.assertFalse(unit.check_expectation(make_report_data(invalid_pub_includes={"bar.h": ["some/header.h"]})))

    def test_check_expectation_for_unexpected_invalid_includes_include(self) -> None:
        unit = make_failure(invalid_includes={"foo.cpp": ["some.h"]})
        self.assertFalse(unit.check_expectation(make_report_data(invalid_priv_includes={"foo.cpp": ["other.h"]})))

    def test_check_expectation_for_expected_unused_deps(self) -> None:
        unit = make_failure(unused_public_deps=["//riff:raff"])
        self.assertTrue(unit.check_expectation(make_report_data(unused_deps=["//riff:raff"])))

    def test_check_expectation_for_unexpected_unused_deps(self) -> None:
        unit = make_failure(unused_public_deps=["//riff:raff"])
        self.assertFalse(unit.check_expectation(make_report_data(unused_deps=["//unexpected:dep"])))

    def test_check_expectation_for_expected_unused_implementation_deps(self) -> None:
        unit = make_failure(unused_private_deps=["//riff:raff"])
        self.assertTrue(unit.check_expectation(make_report_data(unused_impl_deps=["//riff:raff"])))

    def test_check_expectation_for_unexpected_unused_implementation_deps(self) -> None:
        unit = make_failure(unused_private_deps=["//riff:raff"])
        self.assertFalse(unit.check_expectation(make_report_data(unused_impl_deps=["//unexpected:dep"])))

    def test_check_expectation_for_expected_deps_which_should_be_private(self) -> None:
        unit = make_failure(deps_which_should_be_private=["//riff:raff"])
        self.assertTrue(unit.check_expectation(make_report_data(deps_which_should_be_private=["//riff:raff"])))

    def test_check_expectation_for_unexpected_deps_which_should_be_private(self) -> None:
        unit = make_failure(deps_which_should_be_private=["//riff:raff"])
        self.assertFalse(unit.check_expectation(make_report_data(deps_which_should_be_private=["//unexpected:dep"])))

    def test_check_expectation_normalizes_labels(self) -> None:
        unit = make_failure(
            unused_public_deps=["//:foo", "//:bar"],
            unused_private_deps=["@riff//:raff"],
            deps_which_should_be_private=["//:baz"],
        )
        self.assertTrue(
            unit.check_expectation(
                make_report_data(
                    unused_deps=["@@//:foo", "@//:bar"],
                    unused_impl_deps=["@@riff//:raff"],
                    deps_which_should_be_private=["@//:baz"],
                )
            )
        )

    def test_check_expectation_normalizes_paths_for_windows(self) -> None:
        unit = make_failure(invalid_includes={"foo/bar.h": ["header.h"]})
        self.assertTrue(unit.check_expectation(make_report_data(invalid_pub_includes={r"foo\bar.h": ["header.h"]})))
        self.assertTrue(unit.check_expectation(make_report_data(invalid_pub_includes={r"foo\\bar.h": ["header.h"]})))


class ExpectedResultTest(unittest.TestCase):
    def setUp(self) -> None:
        self.reports = Path("reports")

    def _make_report_(self, name: str, data: dict) -> None:
        report = self.reports / name
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(json.dumps(data))

    def test_for_expected_success(self) -> None:
        unit = ExpectedSuccess()

        result = unit.matches_expectation(return_code=0, dwyu_output="", reports_root=self.reports)

        self.assertTrue(result.is_success())

    def test_fail_for_unexpected_failure(self) -> None:
        unit = ExpectedSuccess()

        result = unit.matches_expectation(return_code=1, dwyu_output="", reports_root=self.reports)

        self.assertFalse(result.is_success())
        self.assertEqual(result.error, "unexpected DWYU status code")

    def test_fail_for_unexpected_success(self) -> None:
        unit = ExpectedFailure([])

        result = unit.matches_expectation(return_code=0, dwyu_output="", reports_root=self.reports)

        self.assertFalse(result.is_success())
        self.assertEqual(result.error, "unexpected DWYU status code")

    def test_fail_for_failure_without_dwyu_error(self) -> None:
        unit = ExpectedFailure([])

        result = unit.matches_expectation(return_code=1, dwyu_output="", reports_root=self.reports)

        self.assertFalse(result.is_success())
        self.assertEqual(result.error, "unexpected DWYU status code")

    def test_fail_for_missing_dwyu_report(self) -> None:
        unit = ExpectedFailure(make_failure(target="//:foo"))
        # No report created

        result = unit.matches_expectation(
            return_code=1, dwyu_output=f"{DWYU_FAILURE}\n{DWYU_REPORT} foo.json", reports_root=self.reports
        )

        self.assertFalse(result.is_success())
        self.assertEqual(result.error, "missing DWYU report file: reports/foo.json")

    def test_fail_for_wrong_number_of_dwyu_reports(self) -> None:
        unit = ExpectedFailure([])
        self._make_report_(name="foo.json", data=make_report_data())

        result = unit.matches_expectation(
            return_code=1, dwyu_output=f"{DWYU_FAILURE}\n{DWYU_REPORT} foo.json", reports_root=self.reports
        )

        self.assertFalse(result.is_success())
        self.assertEqual(result.error, "number of DWYU reports does not match expected failures")

    def test_fail_for_unexpected_dwyu_report(self) -> None:
        unit = ExpectedFailure(make_failure(target="//:bar"))
        self._make_report_(name="foo.json", data=make_report_data())

        result = unit.matches_expectation(
            return_code=1, dwyu_output=f"{DWYU_FAILURE}\n{DWYU_REPORT} foo.json", reports_root=self.reports
        )

        self.assertFalse(result.is_success())
        self.assertEqual(result.error, "missing report for expected failure")

    def test_fail_for_unexpected_reported_error(self) -> None:
        unit = ExpectedFailure(make_failure(target="//:foo", unused_public_deps=["//:bar"]))
        self._make_report_(
            name="foo.json", data=make_report_data(analyzed_target="//:foo", unused_deps=["//:unexpected"])
        )

        result = unit.matches_expectation(
            return_code=1, dwyu_output=f"{DWYU_FAILURE}\n{DWYU_REPORT} foo.json", reports_root=self.reports
        )

        self.assertFalse(result.is_success())
        self.assertEqual(result.error, "found unexpected DWYU results")


class TestResult(unittest.TestCase):
    def test_success(self) -> None:
        unit = Success()
        self.assertTrue(unit.is_success())
        self.assertEqual(unit.error, "")

    def test_error(self) -> None:
        unit = Error("foo")
        self.assertFalse(unit.is_success())
        self.assertEqual(unit.error, "foo")


if __name__ == "__main__":
    unittest.main()
