#!/bin/bash

for org in "brit" "carnegie" "cas" "cornell" "field" "harvard" "mo" "nau" "ny" "ufl" "wisc" "wsu"; do
    uv run llama/parse_text.py \
        --ocr-file "data/herbarium/ocr_olmocr2/ocr_${org}_images.csv" \
        --parsed-file "data/herbarium/gemma4_12b_raw/gemma4_12b_${org}.csv" \
        --prompt-md prompts/herbarium_v2.md \
        --model-id "google/gemma-4-12b-qat" \
        --api-host "http://localhost:1234/v1" \
        --temperature 0.1 \
        --timeout 300 \
        --threads 4 \
        --log-file data/herbarium/gemma4_12b_raw/parse_text.log
done
