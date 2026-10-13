import os
import json
import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path


def convert_single(item, output_root):
    """
    Process one manifest entry:
    - Convert audio
    - Return new manifest entry
    """
    uttid = item["uttid"]
    source_path = item["path"]
    instrument = item["instrument"]

    instrument_dir = os.path.join(output_root, instrument)
    os.makedirs(instrument_dir, exist_ok=True)

    new_filename = f"{uttid}.wav"
    new_path = os.path.join(instrument_dir, new_filename)

    cmd = [
        "ffmpeg",
        "-y",
        "-i", source_path,
        "-ac", "1",
        "-ar", "48000",
        "-sample_fmt", "s16",
        new_path
    ]

    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        return {
            "uttid": uttid,
            "path": new_path,
            "source_audio": source_path,
            "instrument": instrument
        }

    except subprocess.CalledProcessError:
        return {
            "uttid": uttid,
            "path": None,
            "source_audio": source_path,
            "instrument": instrument,
            "error": "conversion_failed"
        }


def process_manifest(input_manifest, output_root, output_manifest, num_workers):
    os.makedirs(output_root, exist_ok=True)

    with open(input_manifest, "r") as f:
        items = [json.loads(line.strip()) for line in f]

    results = []

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(convert_single, item, output_root) for item in items]

        for future in as_completed(futures):
            results.append(future.result())

    # Sort according to uttids and write manifest
    results.sort(key=lambda x: x["uttid"])
    with open(output_manifest, "w") as fout:
        for item in results:
            fout.write(json.dumps(item) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multiprocessing audio conversion")
    parser.add_argument("--input_manifest", type=str, required=True)
    parser.add_argument("--output_root", type=str, required=True)
    parser.add_argument("--output_manifest", type=str, required=True)
    parser.add_argument("--num_workers", type=int, default=4)

    args = parser.parse_args()

    process_manifest(
        args.input_manifest,
        args.output_root,
        args.output_manifest,
        args.num_workers
    )