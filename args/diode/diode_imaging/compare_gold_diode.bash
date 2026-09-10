#!/bin/bash

uv run ./llama/reports/compare_output_gold.py \
  --prompt-md prompts/diode_v2.md \
  --gold-file data/diode/diode_imaging/diode_imaging_gpt_nano_2026-06-02a_clean.csv \
  --parse-file data/diode/diode_imaging/diode_imaging_qwen_2026-06-01a_clean.csv \
  --output-csv data/diode/diode_imaging/diode_imaging_nano_vs_qwen_2026-06-02a.csv
