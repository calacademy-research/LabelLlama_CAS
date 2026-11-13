#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 || -z ${1:-} || $1 == */* || $1 == . || $1 == .. ]]; then
    echo "Usage: bash run_ocr_batch.sh BATCH_NAME" >&2
    exit 2
fi

batch=$1
project_dir="$HOME/LabelLlama_CAS"
image_dir="$HOME/ocr_batch/$batch/images"
output_dir="$project_dir/ocr_output"
log_file="$project_dir/ocr_log.txt"

if [[ ! -d "$image_dir" ]]; then
    echo "Missing image directory: $image_dir" >&2
    exit 1
fi

cd "$project_dir"
mkdir -p "$output_dir"
export UV_PROJECT_ENVIRONMENT="${UV_PROJECT_ENVIRONMENT:-.venv-$(hostname -s)-$(uname -m)}"

nohup uv run llama/ocr_images.py \
    --image-glob "$image_dir/*.jpg" \
    --ocr-file "$output_dir/${batch}_ocr.csv" \
    --api-host http://localhost:1234/v1 \
    --threads 1 \
    --max-tokens 2048 \
    --model chandra-ocr \
    </dev/null >"$log_file" 2>&1 &

printf 'OCR batch %s launched (PID %s). Log: %s\n' "$batch" "$!" "$log_file"