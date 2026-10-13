import os
import json
import argparse
from multiprocessing import Pool, cpu_count
from functools import partial

import soundfile as sf


SEGMENT_DURATION = 10  # seconds


def segment_audio(entry, output_dir):
    """
    Process a single manifest entry:
    - Load audio
    - Split into 10s chunks
    - Save segments
    - Return updated manifest entries
    """

    input_path = entry["path"]
    instrument = entry["instrument"]
    uttid = entry["uttid"]

    try:
        audio, sr = sf.read(input_path)
    except Exception as e:
        print(f"Error reading {input_path}: {e}")
        return []

    total_samples = len(audio)
    segment_samples = SEGMENT_DURATION * sr

    segments = []
    base_out_dir = os.path.join(output_dir, instrument)
    os.makedirs(base_out_dir, exist_ok=True)

    seg_idx = 1
    for start in range(0, total_samples, segment_samples):
        end = start + segment_samples
        if end > total_samples:
            break  # drop last short segment (can change if needed)

        segment_audio = audio[start:end]

        segment_id = f"{uttid}_utt_{seg_idx:04d}"
        segment_filename = f"{segment_id}.wav"
        segment_path = os.path.join(base_out_dir, segment_filename)

        try:
            sf.write(segment_path, segment_audio, sr)
        except Exception as e:
            print(f"Error writing {segment_path}: {e}")
            continue

        # Create new manifest entry
        new_entry = dict(entry)  # copy original
        new_entry["utt_path"] = new_entry.pop("path")
        new_entry["segment_id"] = segment_id
        new_entry["segment_path"] = segment_path

        segments.append(new_entry)
        seg_idx += 1

    return segments


def process_manifest(input_manifest, output_manifest_path, output_dir, num_workers):
    with open(input_manifest, "r") as f:
        lines = [json.loads(line.strip()) for line in f]

    print(f"Loaded {len(lines)} entries")

    worker_fn = partial(segment_audio, output_dir=output_dir)

    with Pool(num_workers) as pool:
        results = pool.map(worker_fn, lines)

    # Flatten results
    all_segments = [seg for sublist in results for seg in sublist]

    print(f"Generated {len(all_segments)} segments")

    os.makedirs(os.path.dirname(output_manifest_path), exist_ok=True)

    # Sort by utt_id, segment_id to be deterministic
    all_segments.sort(key=lambda x: (x["uttid"], x["segment_id"]))

    with open(output_manifest_path, "w") as f:
        for entry in all_segments:
            f.write(json.dumps(entry) + "\n")

    print(f"Saved new manifest → {output_manifest_path}")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input_manifest", type=str, required=True)
    parser.add_argument("--output_manifest", type=str, required=True)
    parser.add_argument("--output_dir", type=str, required=True)
    parser.add_argument("--num_workers", type=int, default=cpu_count())

    args = parser.parse_args()

    process_manifest(
        args.input_manifest,
        args.output_manifest,
        args.output_dir,
        args.num_workers
    )


if __name__ == "__main__":
    main()