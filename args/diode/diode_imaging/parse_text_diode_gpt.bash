#!/bin/bash

uv run llama/parse_text.py \
  --ocr-file data/diode/diode_imaging/diode_imaging_2026-05-26.csv \
  --parsed-file data/diode/diode_imaging/diode_imaging_gpt_nano_2026-06-02a.csv \
  --prompt-md prompts/diode_v2.md \
  --model-id "gpt-5-nano-2025-08-07" \
  --threads 20 \
  --log-file data/diode/diode_imaging/diode_imaging_gpt_nano.log
