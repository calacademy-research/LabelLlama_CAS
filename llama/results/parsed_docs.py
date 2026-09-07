import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import pandas as pd

from llama.results.model_status import ModelStatus
from llama.results.ocr_docs import read_results_csv

if TYPE_CHECKING:
    from pathlib import Path

    from llama.results.model_status import StatusCounts


REQUIRED_OCR_COLUMNS = {"source", "text"}


@dataclass
class ParsedDocs:
    ocr_file: Path | None = None
    ocr_records: list[dict] = field(default_factory=list[dict])
    parsed_file: Path | None = None
    file_mode: str = "w"
    parsed_records: list[dict] = field(default_factory=list[dict])
    already_done: set[str] = field(default_factory=set[str])
    tasks: list[dict] = field(default_factory=list[dict])
    limit: int | None = None

    def __init__(
        self,
        parsed_file: Path,
        ocr_file: Path,
        limit: int | None = None,
        expected_columns: list[str] | None = None,
    ) -> None:
        self.ocr_file = ocr_file
        self.parsed_file = parsed_file
        self.limit = limit

        self.ocr_records = self._read_ocr_records(ocr_file)
        self.ocr_records = self.ocr_records[:limit]

        self.parsed_records, self.file_mode = self._read_parsed_records(
            parsed_file, expected_columns
        )
        self.already_done = self._get_already_parsed()
        self.tasks = self._get_tasks()

    @property
    def input_len(self) -> int:
        return len(self.ocr_records)

    def _read_ocr_records(self, ocr_file: Path) -> list[dict]:
        df = pd.read_csv(ocr_file, dtype=str).fillna("")
        missing = REQUIRED_OCR_COLUMNS - set(df.columns)
        if missing:
            missing_str = ", ".join(sorted(missing))
            raise ValueError(f"OCR file is missing required columns: {missing_str}")
        return df.to_dict("records")

    def _read_parsed_records(
        self,
        parsed_file: Path | None,
        expected_columns: list[str] | None = None,
    ) -> tuple[list[dict], str]:
        mode = "w"
        records = []
        if parsed_file and parsed_file.exists() and parsed_file.stat().st_size > 0:
            df = read_results_csv(parsed_file, "existing parsed file")
            if (
                df is not None
                and expected_columns
                and list(df.columns) != expected_columns
            ):
                raise ValueError(
                    "Existing parsed file columns do not match the prompt columns"
                )
            mode = "a"
            records = df.to_dict("records")
        return records, mode

    def _get_already_parsed(self) -> set[str]:
        return {
            r["source"]
            for r in self.parsed_records
            if r["status"] == ModelStatus.SUCCESS
        }

    def _get_tasks(self) -> list[dict]:
        return sorted(
            [r for r in self.ocr_records if r["source"] not in self.already_done],
            key=lambda r: r["source"],
        )

    def log_what_to_do(self) -> None:
        logging.info(f"There are {self.input_len} documents to process")
        logging.info(f"{len(self.already_done)} documents were already done.")
        if self.limit:
            logging.info(f"Limited to {self.limit} documents.")
        logging.info(f"There are {len(self.tasks)} documents left to process.")

    def log_what_was_done(self, statuses: StatusCounts) -> None:
        logging.info(
            f"Total {len(self.tasks)} documents processed "
            f"with {statuses.get(ModelStatus.ERROR)} errors "
            f"and {len(self.already_done)} documents skipped."
        )
