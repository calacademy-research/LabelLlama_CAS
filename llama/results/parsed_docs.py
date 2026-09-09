from typing import TYPE_CHECKING

import pandas as pd

from llama.results.model_status import ModelStatus
from llama.results.ocr_docs import read_results_csv

if TYPE_CHECKING:
    from pathlib import Path


REQUIRED_OCR_COLUMNS = {"source", "text"}


class ParsedDocs:
    def __init__(
        self,
        parsed_file: Path,
        ocr_file: Path,
        limit: int | None = None,
        expected_columns: list[str] | None = None,
    ) -> None:
        ocr_recs = self.read_ocr_records(ocr_file)

        self.parsed_records, self.file_mode = self.read_parsed_records(
            parsed_file, expected_columns
        )
        already_done = {
            r.get("source")
            for r in self.parsed_records
            if r.get("source") and r.get("status", "").lower() == ModelStatus.SUCCESS
        }
        tasks = [
            rec for rec in ocr_recs if (rec.get("source") or "") not in already_done
        ]
        tasks = sorted(tasks, key=lambda rec: rec.get("source", ""))
        self.tasks = tasks[:limit]

    def read_ocr_records(self, ocr_file: Path) -> list[dict]:
        try:
            df = pd.read_csv(ocr_file, dtype=str).fillna("")
        except pd.errors.EmptyDataError:
            return []

        missing = REQUIRED_OCR_COLUMNS - set(df.columns)
        if missing:
            missing_str = ", ".join(sorted(missing))
            raise ValueError(f"OCR file is missing required columns: {missing_str}")
        return df.to_dict("records")

    def read_parsed_records(
        self,
        parsed_file: Path | None,
        expected_columns: list[str] | None = None,
    ) -> tuple[list[dict], str]:
        mode = "w"
        records = []
        if parsed_file and parsed_file.exists() and parsed_file.stat().st_size > 0:
            df = read_results_csv(parsed_file, "existing parsed file")
            if df is None:
                return records, mode
            if expected_columns and list(df.columns) != expected_columns:
                raise ValueError(
                    "Existing parsed file columns do not match the prompt columns"
                )
            mode = "a"
            records = df.to_dict("records")
        return records, mode
