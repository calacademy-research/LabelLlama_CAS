#!/bin/bash

uv run ./llama/reports/compare_output_gold.py \
  --prompt-md prompts/diode_v2.md \
  --gold-file data/diode/gold_std/Abbott_and_Ware_gold.csv \
  --parse-file data/diode/gold_std/gold_gpt_nano_2026-06-02a_clean.csv \
  --output-csv data/diode/gold_std/gold_vs_gpt_nano_2026-06-02a.csv
