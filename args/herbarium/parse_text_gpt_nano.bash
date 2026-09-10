#!/bin/bash

# for org in "brit" "carnegie" "cas" "cornell" "field" "harvard" "mo" "nau" "ny" "ufl" "wisc" "wsu"; do
for org in "nau"; do
    uv run llama/parse_text.py \
        --ocr-file "data/herbarium/ocr_olmocr2/ocr_${org}_images.csv" \
        --parsed-file "data/herbarium/gpt_nano_raw/gpt_nano_${org}.csv" \
        --prompt-md prompts/herbarium_v2.md \
        --model-id "gpt-5-nano-2025-08-07" \
        --api-host "https://api.openai.com/v1" \
        --threads 20 \
        --log-file data/herbarium/gpt_nano_raw/parse_text_gpt_nano.log
done
