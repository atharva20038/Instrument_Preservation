#!/bin/bash

python timber_analysis.py \
    --real_manifest "/workspace/idp/data_16k/real_manifest_segmented.jsonl" \
    --gen_manifest "/workspace/idp/data_16k/mustango_manifest.jsonl" \
    --output_file "/workspace/idp/output_timbre/timbre_analysis_mustango_rerun.json"