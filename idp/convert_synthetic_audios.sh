# convert musicgen audios
python convert_synthetic_audios.py \
    --input_manifest /workspace/synthetic_data/musicgen_manifest.jsonl \
    --output_root /workspace/idp/data/raw/musicgen \
    --output_manifest /workspace/idp/data/musicgen_manifest.jsonl \
    --num_workers 16

# convert mustango audios
python convert_synthetic_audios.py \
    --input_manifest /workspace/synthetic_data/mustango_manifest.jsonl \
    --output_root /workspace/idp/data/raw/mustango \
    --output_manifest /workspace/idp/data/mustango_manifest.jsonl \
    --num_workers 16

# convert lyria audios
python convert_synthetic_audios.py \
    --input_manifest /workspace/synthetic_data/lyria_manifest.jsonl \
    --output_root /workspace/idp/data/raw/lyria \
    --output_manifest /workspace/idp/data/lyria_manifest.jsonl \
    --num_workers 16

# convert suno audios
python convert_synthetic_audios.py \
    --input_manifest /workspace/synthetic_data/suno_manifest.jsonl \
    --output_root /workspace/idp/data/raw/suno \
    --output_manifest /workspace/idp/data/suno_manifest.jsonl \
    --num_workers 16