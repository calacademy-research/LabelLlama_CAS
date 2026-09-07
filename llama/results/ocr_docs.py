import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

import pandas as pd

from llama.pylib import image_util
from llama.results.model_status import ModelStatus

if TYPE_CHECKING:
    from pathlib import Path

    from llama.results.model_status import StatusCounts


COLUMNS = ["status", "source", "elapsed", "text"]


def read_results_csv(path: Path, label: str) -> pd.DataFrame | None:
    """
    Read a results CSV into a DataFrame of strings.

    Returns None when the file holds no parseable content (the caller can
    then safely start the file over). Raises ValueError when the file exists
    but cannot be read as CSV, so a corrupt file is never silently
    overwritten.
    """
    try:
        return pd.read_csv(path, dtype=str).fillna("")
    except pd.errors.EmptyDataError:
        return None
    except (pd.errors.ParserError, UnicodeDecodeError) as err:
        raise ValueError(f"{label} is not a readable CSV file: {path} ({err})") from err


@dataclass
class OcrDocs:
    # -------------- ClassVars ---------------
    columns: ClassVar[list[str]] = COLUMNS
    # ----------------------------------------

    ocr_file: Path | None = None
    file_mode: str = "w"
    ocr_records: list[dict] = field(default_factory=list[dict])
    already_done: set[str] = field(default_factory=set[str])
    tasks: list[Path] = field(default_factory=list)
    limit: int | None = None

    def __init__(
        self,
        image_dir: Path,
        image_glob: str = "",
        ocr_file: Path | None = None,
        input_file: Path | None = None,
        limit: int | None = None,
    ) -> None:
        self.ocr_file = ocr_file
        self.limit = limit

        self.image_paths = image_util.get_images(image_dir, image_glob)
        self.image_paths = self.image_paths[:limit]

        self.ocr_records, self.file_mode = self._read_ocr_records(ocr_file)
        self.already_done = self._get_already_read()
        self.tasks = self._get_tasks(input_file)

    @property
    def input_len(self) -> int:
        return len(self.image_paths)

    def _read_ocr_records(self, ocr_file: Path | None) -> tuple[list[dict], str]:
        mode = "w"
        records = []
        if ocr_file and ocr_file.exists():
            df = read_results_csv(ocr_file, "OCR file")
            if df is not None:
                missing = set(COLUMNS) - set(df.columns)
                if missing:
                    missing_str = ", ".join(sorted(missing))
                    msg = f"OCR file is missing required columns: {missing_str}"
                    raise ValueError(msg)
            mode = "a"
            records = df.to_dict("records")
        return records, mode

    def _get_already_read(self) -> set[str]:
        return {
            r.get("source", "")
            for r in self.ocr_records
            if r.get("source") and r.get("status", "").lower() == ModelStatus.SUCCESS
        }

    def _get_tasks(self, input_file: Path | None) -> list[Path]:
        tasks = sorted(p for p in self.image_paths if str(p) not in self.already_done)
        if input_file:
            tasks += [
                s
                for s in image_util.read_sources(input_file)
                if str(s) not in self.already_done
            ]
        return tasks

    @staticmethod
    def get_ocr_records(ocr_file: Path | None) -> list[dict]:
        return (
            pd.read_csv(ocr_file, dtype=str).fillna("").to_dict("records")
            if ocr_file
            else []
        )

    def log_what_to_do(self) -> None:
        logging.info(f"There are {self.input_len} images to process")
        logging.info(f"{len(self.already_done)} images were already done.")
        if self.limit:
            logging.info(f"Limited to {self.limit} images.")
        logging.info(f"There are {len(self.tasks)} images left to process.")

    def log_what_was_done(self, statuses: StatusCounts) -> None:
        logging.info(
            f"Total {len(self.tasks)} images processed "
            f"with {statuses.get(ModelStatus.ERROR)} errors "
            f"and {len(self.already_done)} images skipped."
        )
