#!/bin/bash

uv run ./llama/ocr_images.py \
  --image-dir data/diode/diode_imaging/images \
  --ocr-file data/diode/diode_imaging/diode_imaging_2026-05-26.csv \
  --model-id chandra-ocr \
  --max-tokens 2048 \
  --prompt-md prompts/ocr_v1.md \
  --threads 2 \
  --notes "A new batch of diode images to OCR" \
  --image-glob "*_card" \
  --log-file data/diode/diode_imaging/ode_imaging_2026-05-26.log
