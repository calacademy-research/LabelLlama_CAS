#!/bin/bash

uv run llama/parse_text.py \
  --ocr-file data/diode/gold_std/gold_docs_2026-05-11.csv \
  --parsed-file data/diode/gold_std/gold_qwen_2026-06-02a.csv \
  --prompt-md prompts/diode_v2.md \
  --model-id "qwen/qwen3.6-35b-a3b" \
  --api-host "http://localhost:1234/v1" \
  --temperature 0.0 \
  --threads 4 \
  --log-file data/diode/gold_std/gold_std.log
