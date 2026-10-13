#!/bin/bash

python pitch_analysis_path.py \
  --real_manifest /workspace/idp/data_16k/real_manifest_segmented.jsonl \
  --gen_manifest /workspace/idp/data_16k/mustango_manifest.jsonl \
  --output_file /workspace/idp/output_pitch/pitch_analysis_mustango.json
