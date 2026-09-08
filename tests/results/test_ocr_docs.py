import csv
import os
import tempfile
import unittest
from pathlib import Path

from llama.results.model_status import StatusCounts
from llama.results.ocr_docs import OcrDocs, read_results_csv

PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts"


def write_csv(path: Path, header: list[str], rows: list[list]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


class TestOcrDocs(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.a = self.tmp / "a.png"
        self.b = self.tmp / "b.jpg"
        self.a.write_bytes(b"png")
        self.b.write_bytes(b"jpg")
        (self.tmp / "notes.txt").write_text("not an image")

    def test_read_results_csv_basic_01(self) -> None:
        path = self.tmp / "res.csv"
        write_csv(
            path,
            ["status", "source", "elapsed", "text"],
            [["success", "a.png", "1.0", "hello"], ["ERROR", "b.png", "", ""]],
        )

        df = read_results_csv(path, "OCR file")

        assert df is not None
        # Missing cells become "", everything stays a string
        assert df.iloc[1]["elapsed"] == ""
        assert df.iloc[0]["text"] == "hello"
        assert isinstance(df.iloc[0]["elapsed"], str)

    def test_read_results_csv_empty_file_returns_none_02(self) -> None:
        path = self.tmp / "empty.csv"
        path.write_bytes(b"")

        assert read_results_csv(path, "OCR file") is None

    def test_read_results_csv_corrupt_raises_value_error_03(self) -> None:
        path = self.tmp / "bad.csv"
        # Unbalanced quote -> pandas ParserError
        path.write_text('status,source\n"unterminated,2\n', encoding="utf-8")

        with self.assertRaises(ValueError) as ctx:
            read_results_csv(path, "OCR file")

        # The label and the path help the user find the bad file
        assert "OCR file" in str(ctx.exception)
        assert str(path) in str(ctx.exception)

    def test_read_results_csv_bad_encoding_raises_04(self) -> None:
        path = self.tmp / "bin.csv"
        path.write_bytes(b"\xff\xfe\x00\x81\n\x00")

        with self.assertRaises(ValueError):
            read_results_csv(path, "OCR file")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_init_without_ocr_file_05(self) -> None:
        docs = OcrDocs(self.tmp, ocr_file=self.tmp / "ocr.csv")

        assert docs.file_mode == "w"
        assert docs.ocr_records == []
        assert docs.already_done == set()
        assert docs.input_len == 2
        assert docs.tasks == [self.a, self.b]

    def test_init_missing_columns_raises_07(self) -> None:
        ocr_file = self.tmp / "ocr.csv"
        write_csv(ocr_file, ["status", "source"], [["success", "a.png"]])

        with self.assertRaises(ValueError) as ctx:
            OcrDocs(self.tmp, ocr_file=ocr_file)

        assert "text" in str(ctx.exception)

    def test_log_what_was_done_15(self) -> None:
        docs = OcrDocs(self.tmp, ocr_file=self.tmp / "o.csv")
        statuses = StatusCounts()
        statuses.count("error")

        with self.assertLogs(level="INFO") as log:
            docs.log_what_was_done(statuses)

        assert "2 images processed" in log.output[0]
        assert "1 errors" in log.output[0]

    def test_init_with_existing_ocr_file_16(self) -> None:
        ocr_file = self.tmp / "ocr.csv"
        write_csv(
            ocr_file,
            ["status", "source", "elapsed", "text"],
            [
                ["success", str(self.a), "1.0", "ok"],
                ["ERROR", str(self.b), "0.5", "boom"],
            ],
        )

        docs = OcrDocs(self.tmp, ocr_file=ocr_file)

        # Append mode, records kept, only successes count as done
        assert docs.file_mode == "a"
        assert len(docs.ocr_records) == 2
        assert docs.already_done == {str(self.a)}
        # The failed image is scheduled again, the success is not
        assert docs.tasks == [self.b]

    def test_relative_sources_are_recognized_18(self) -> None:
        # RED: a previous run stored sources in the CSV exactly as they
        # were written, but _get_tasks compares Path objects against the
        # string set already_done (Path(p) not in self.already_done),
        # which is never True, so finished images are re-OCRed.
        # Suggested fix (ocr_docs.py): compare `str(p) not in
        # self.already_done`.
        ocr_file = self.tmp / "ocr.csv"
        write_csv(
            ocr_file,
            ["status", "source", "elapsed", "text"],
            [["success", "a.png", "1.0", "ok"]],
        )
        old_cwd = Path.cwd()
        os.chdir(self.tmp)
        self.addCleanup(os.chdir, old_cwd)

        docs = OcrDocs(Path(), ocr_file=ocr_file)

        assert docs.tasks == [Path("b.jpg")]


if __name__ == "__main__":
    unittest.main()
