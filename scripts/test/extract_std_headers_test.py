import unittest

from scripts.extract_std_headers import extract_header


class TestExtractHeader(unittest.TestCase):
    def test_empty_input_yields_empty_list(self) -> None:
        self.assertEqual(extract_header(""), [])

    def test_extracting_headers(self) -> None:
        headers = extract_header(
            """
unrelated_stuff
<foo>
ignore this
<bar.h>
<multiple_header><in_one_line>
        """.strip()
        )

        self.assertEqual(headers, ["foo", "bar.h", "multiple_header", "in_one_line"])


if __name__ == "__main__":
    unittest.main()
