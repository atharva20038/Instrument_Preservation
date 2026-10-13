# # real data
# python create_segments.py \
#     --input_manifest /workspace/idp/data/real_manifest.jsonl \
#     --output_manifest /workspace/idp/data/real_manifest_segmented.jsonl \
#     --output_dir /workspace/idp/data/segmented/real \
#     --num_workers 16

# # lyria
# python create_segments.py \
#     --input_manifest /workspace/idp/data/lyria_manifest.jsonl \
#     --output_manifest /workspace/idp/data/lyria_manifest_segmented.jsonl \
#     --output_dir /workspace/idp/data/segmented/lyria \
#     --num_workers 16

# # suno
# python create_segments.py \
#     --input_manifest /workspace/idp/data/suno_manifest.jsonl \
#     --output_manifest /workspace/idp/data/suno_manifest_segmented.jsonl \
#     --output_dir /workspace/idp/data/segmented/suno \
#     --num_workers 16

# mert data
python create_segments.py \
    --input_manifest /workspace/mert_ft/data/real_manifest.jsonl \
    --output_manifest /workspace/mert_ft/data/real_manifest_segmented.jsonl \
    --output_dir /workspace/mert_ft/data/segmented \
    --num_workers 16
