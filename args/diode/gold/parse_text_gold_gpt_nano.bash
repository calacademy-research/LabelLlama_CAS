#!/bin/bash

uv run llama/parse_text.py \
  --ocr-file data/diode/gold_std/gold_docs_2026-05-11.csv \
  --parsed-file data/diode/gold_std/gold_gpt_nano_2026-06-02a.csv \
  --prompt-md prompts/diode_v2.md \
  --model-id "gpt-5-nano-2025-08-07" \
  --threads 20 \
  --log-file data/diode/gold_std/gold_std.log
