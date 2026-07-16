#!/usr/bin/env bash

set -euo pipefail

echo "[$(date)] Starting run_llm.sh"

echo "[$(date)] Activating virtual environment..."
source .venv/bin/activate
echo "[$(date)] Virtual environment activated."


API_KEY="${OPENAI_API_KEY:-}"

if [ -z "$API_KEY" ]; then
    echo "ERROR: OPENAI_API_KEY is not set."
    echo "Run: export OPENAI_API_KEY='your_api_key_here'"
    exit 1
fi

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <input_docs_csv> <output_extracts_csv>"
    echo
    echo "Example:"
    echo "  $0 ocr_output/ocr_demo_docs.csv ocr_output/lm_extracts.csv"
    exit 1
fi

OCR_DOCS_CSV="$1"
LM_EXTRACTS_CSV="$2"

echo "[$(date)] Input OCR CSV: $OCR_DOCS_CSV"
echo "[$(date)] Output extraction CSV: $LM_EXTRACTS_CSV"

# create cleaned filename automatically
BASE_NAME="${LM_EXTRACTS_CSV%.csv}"
CLEANED_OUTPUT_CSV="${BASE_NAME}_cleaned.csv"

echo "[$(date)] Cleaned output CSV will be: $CLEANED_OUTPUT_CSV"

echo "[$(date)] Starting LLM extraction step..."


uv run llama/parse_text.py \
    --ocr-file "$OCR_DOCS_CSV" \
    --parse-file "$LM_EXTRACTS_CSV" \
    --prompt prompts/fields/herbarium.md \
    --api-host https://api.openai.com/v1 \
    --model gpt-5-nano \
    --threads 2

echo "[$(date)] LLM extraction completed."

#uv run llama/postprocess.py \
#    --in-file "$LM_EXTRACTS_CSV" \
#    --out-file "$CLEANED_OUTPUT_CSV" \
#    --run-field-models

#echo "[$(date)] Postprocessing completed."

#echo "[$(date)] Script finished successfully."