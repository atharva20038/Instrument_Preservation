#!/bin/bash

python pitch_analysis.py \
  --real_manifest /workspace/idp/data_16k/real_manifest_segmented.jsonl \
  --gen_manifest /workspace/idp/data_16k/suno_manifest_segmented.jsonl \
  --output_file /workspace/idp/output_pitch/pitch_analysis_suno.json
