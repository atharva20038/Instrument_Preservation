# convert real audios
python convert_audios.py \
    --input_manifest /workspace/yt_data/manifest.jsonl \
    --output_root /workspace/idp/data/raw/real \
    --output_manifest /workspace/idp/data/real_manifest.jsonl \
    --num_workers 16

# mert data
# python convert_audios.py \
#     --input_manifest /workspace/yt_data/manifest.jsonl \
#     --output_root /workspace/mert_ft/data/real \
#     --output_manifest /workspace/mert_ft/data/real_manifest.jsonl \
#     --num_workers 16