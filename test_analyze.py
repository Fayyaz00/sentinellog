import contextlib
import io
import unittest

from analyze import analyze_lines, print_summary


class LogAnalysisTests(unittest.TestCase):
    def test_counts_levels_and_groups_errors_with_line_numbers(self):
        lines = [
            "2026-01-10 14:35:00 INFO auth Login attempt\n",
            "2026-01-10 14:35:01 WARNING auth Invalid credentials\n",
            "2026-01-10 14:35:02 ERROR auth Database failed\n",
            "2026-01-10 14:35:03 ERROR api Database failed\n",
        ]
        summary = analyze_lines(lines)
        self.assertEqual(summary.total, 4)
        self.assertEqual(dict(summary.counts), {"INFO": 1, "WARN": 1, "ERROR": 2})
        error = summary.errors["Database failed"]
        self.assertEqual(error.count, 2)
        self.assertEqual(error.example_lines, [3, 4])

    def test_unrecognized_lines_are_preserved_in_output(self):
        summary = analyze_lines(["not a recognized log\n", "\n"])
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            print_summary(summary)
        self.assertEqual(summary.unrecognized_count, 2)
        self.assertEqual(summary.unrecognized_examples, [(1, "not a recognized log"), (2, "")])
        self.assertIn("1: not a recognized log", output.getvalue())
        self.assertIn("Unrecognized: 2", output.getvalue())

    def test_message_containing_error_is_not_a_severity(self):
        summary = analyze_lines(["2026-01-10 14:35:00 INFO api Previous ERROR cleared\n"])
        self.assertEqual(summary.counts["INFO"], 1)
        self.assertEqual(summary.counts["ERROR"], 0)

    def test_empty_input(self):
        summary = analyze_lines([])
        self.assertEqual(summary.total, 0)
        self.assertFalse(summary.errors)

    def test_repeated_lines_have_exact_counts_and_limited_examples(self):
        error = "2026-01-10 14:35:00 ERROR api Database failed\n"
        summary = analyze_lines([error] * 10 + ["unknown\n"] * 10)

        self.assertEqual(summary.errors["Database failed"].count, 10)
        self.assertEqual(summary.errors["Database failed"].example_lines, [1, 2, 3, 4, 5])
        self.assertEqual(summary.unrecognized_count, 10)
        self.assertEqual(len(summary.unrecognized_examples), 5)


if __name__ == "__main__":
    unittest.main()
