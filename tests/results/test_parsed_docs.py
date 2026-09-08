import csv
import tempfile
import unittest
from pathlib import Path

from llama.results.model_status import StatusCounts
from llama.results.parsed_docs import ParsedDocs

COLUMNS = ["status", "source", "elapsed", "text"]


def write_csv(path: Path, header: list[str], rows: list[list]) -> None:

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


class TestParsedDocs(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

        # Sources are deliberately out of order
        self.ocr_file = self.tmp / "ocr.csv"
        write_csv(
            self.ocr_file,
            COLUMNS,
            [
                ["ERROR", "b.txt", "1.0", "text b"],
                ["success", "a.txt", "1.0", "text a"],
                ["success", "c.txt", "1.0", "text c"],
            ],
        )
        self.parsed_file = self.tmp / "parsed.csv"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_ocr_file_missing_column_raises_01(self) -> None:
        bad_ocr = self.tmp / "bad_ocr.csv"
        write_csv(bad_ocr, ["source", "elapsed"], [["a.txt", "1.0"]])

        with self.assertRaises(ValueError) as ctx:
            ParsedDocs(self.parsed_file, bad_ocr)

        assert "text" in str(ctx.exception)

    def test_new_parsed_file_uses_write_mode_02(self) -> None:
        docs = ParsedDocs(self.parsed_file, self.ocr_file)

        assert docs.file_mode == "w"
        assert docs.parsed_records == []
        assert docs.already_done == set()
        assert docs.input_len == 3
        assert [t["source"] for t in docs.tasks] == [
            "a.txt",
            "b.txt",
            "c.txt",
        ]

    def test_tasks_sorted_by_source_03(self) -> None:
        # The OCR file lists b, a, c; tasks come back sorted by source
        docs = ParsedDocs(self.parsed_file, self.ocr_file)

        sources = [t["source"] for t in docs.tasks]
        assert sources == sorted(sources)

    def test_resume_appends_and_skips_successes_04(self) -> None:
        write_csv(
            self.parsed_file,
            COLUMNS,
            [
                ["success", "a.txt", "2.0", "parsed a"],
                ["ERROR", "b.txt", "2.0", "boom"],
            ],
        )

        docs = ParsedDocs(self.parsed_file, self.ocr_file, expected_columns=COLUMNS)

        # Existing results are kept and appended to
        assert docs.file_mode == "a"
        assert len(docs.parsed_records) == 2
        # Only successes are skipped; the error is scheduled again
        assert docs.already_done == {"a.txt"}
        assert [t["source"] for t in docs.tasks] == ["b.txt", "c.txt"]

    def test_column_mismatch_raises_05(self) -> None:
        write_csv(
            self.parsed_file,
            COLUMNS,
            [["success", "a.txt", "2.0", "parsed a"]],
        )

        with self.assertRaises(ValueError) as ctx:
            ParsedDocs(
                self.parsed_file,
                self.ocr_file,
                expected_columns=["status", "source", "text"],
            )

        assert "do not match" in str(ctx.exception)

    def test_no_expected_columns_skips_check_06(self) -> None:
        # Without expected_columns any existing file is resumed as-is
        write_csv(
            self.parsed_file,
            ["status", "source"],
            [["success", "a.txt"]],
        )

        docs = ParsedDocs(self.parsed_file, self.ocr_file)

        assert docs.file_mode == "a"
        assert docs.already_done == {"a.txt"}

    def test_corrupt_parsed_file_raises_07(self) -> None:
        # Unbalanced quote -> pandas ParserError -> clean ValueError
        self.parsed_file.write_text(
            'status,source\n"unterminated,2\n', encoding="utf-8"
        )

        with self.assertRaises(ValueError) as ctx:
            ParsedDocs(self.parsed_file, self.ocr_file)

        assert "existing parsed file" in str(ctx.exception)

    def test_header_only_parsed_file_08(self) -> None:
        # A file with only the header row resumes with no records
        write_csv(self.parsed_file, COLUMNS, [])

        docs = ParsedDocs(self.parsed_file, self.ocr_file, expected_columns=COLUMNS)

        assert docs.file_mode == "a"
        assert docs.parsed_records == []
        assert docs.already_done == set()
        assert len(docs.tasks) == 3

    def test_limit_applied_to_ocr_records_09(self) -> None:
        docs = ParsedDocs(self.parsed_file, self.ocr_file, limit=2)

        assert docs.input_len == 2
        assert [t["source"] for t in docs.tasks] == ["a.txt", "b.txt"]

    def test_parsed_file_with_no_content_10(self) -> None:
        # Handle an invalid data frame
        self.parsed_file.write_text("\n", encoding="utf-8")

        docs = ParsedDocs(self.parsed_file, self.ocr_file)

        assert docs.file_mode == "w"
        assert docs.parsed_records == []
        assert len(docs.tasks) == 3

    def test_log_what_to_do_11(self) -> None:
        docs = ParsedDocs(self.parsed_file, self.ocr_file, limit=2)

        with self.assertLogs(level="INFO") as log:
            docs.log_what_to_do()

        output = "\n".join(log.output)
        assert "2 documents to process" in output
        assert "Limited to 2 documents." in output
        assert "2 documents left to process" in output

    def test_log_what_was_done_12(self) -> None:
        docs = ParsedDocs(self.parsed_file, self.ocr_file)
        statuses = StatusCounts()
        statuses.count("error")
        statuses.count("success")

        with self.assertLogs(level="INFO") as log:
            docs.log_what_was_done(statuses)

        assert "3 documents processed" in log.output[0]
        assert "1 errors" in log.output[0]


if __name__ == "__main__":
    unittest.main()
