import os
import argparse
import subprocess

def convert_audio(input_path, output_path, sample_rate):
    # check if output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-ac", "1",                
        "-ar", str(sample_rate),    
        "-sample_fmt", "s16",       
        output_path
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"Converted: {input_path} -> {output_path}")

    except subprocess.CalledProcessError:
        print(f"Conversion failed: {input_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Single audio conversion using ffmpeg")

    parser.add_argument("--input_path", type=str, required=True, help="Path to input audio")
    parser.add_argument("--output_path", type=str, required=True, help="Path to save converted audio")
    parser.add_argument("--sample_rate", type=int, default=16000, help="Target sampling rate (e.g., 16000, 44100, 48000)")

    args = parser.parse_args()

    convert_audio(
        args.input_path,
        args.output_path,
        args.sample_rate
    )