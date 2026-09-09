#!/usr/bin/env python3

import argparse
import textwrap
from collections import defaultdict
from pathlib import Path

import pandas as pd

from llama.pylib import log
from llama.results.model_status import ModelStatus

REQUIRED_COLUMNS = {"source", "text"}


def compare(args: argparse.Namespace) -> None:
    """Group OCR results by source and print each model run's text."""
    job_began = log.job_began(None, args=args)

    all_ocr = defaultdict(list)
    for ocr_file in args.ocr_file:
        df = pd.read_csv(ocr_file, dtype=str).fillna("")

        missing = REQUIRED_COLUMNS - set(df.columns)
        if missing:
            missing_str = ", ".join(sorted(missing))
            raise ValueError(
                f"OCR file {ocr_file} is missing required columns: {missing_str}"
            )

        has_status = "status" in df.columns
        for row in df.to_dict("records"):
            if has_status and not ModelStatus.is_success(row.get("status", "")):
                continue
            tagged = {"file": ocr_file.stem, **row}
            others = [r for r in all_ocr[row["source"]] if r["file"] != ocr_file.stem]
            all_ocr[row["source"]] = [*others, tagged]

    sources = sorted(all_ocr)
    for i, key in enumerate(sources[: args.limit], 1):
        print("=" * 90)
        print(i, key)
        print()
        for row in all_ocr[key]:
            print(f"### {row['file']}  (elapsed {row.get('elapsed', '')})")
            print(row["text"])
            print("-" * 80)
        print()

    log.job_elapsed(job_began)


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent("""Compare OCR results from different models."""),
    )
    arg_parser.add_argument(
        "--ocr-file",
        type=Path,
        required=True,
        action="append",
        metavar="path",
        help="""OCR results CSV for one model run. Pass this flag once per
            model.""",
    )
    arg_parser.add_argument(
        "--limit",
        type=int,
        metavar="int",
        help="""Limit to this many records.""",
    )
    ns = arg_parser.parse_args(args)
    return ns


if __name__ == "__main__":
    ARGS = parse_args()
    compare(ARGS)
