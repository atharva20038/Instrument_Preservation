import os
import json
import base64
import time
from tqdm import tqdm
from google import genai
from google.genai import types

def create_synthetic_data(prompts, client, audio_save_paths):
    max_retries = 5
    for i, prompt in enumerate(prompts):
        if os.path.exists(audio_save_paths[i]):
            print(f"\n[SKIP] Audio already exists: {audio_save_paths[i]}")
            continue
        for attempt in range(1, max_retries + 1):
            try:
                response = client.models.generate_content(
                    model="lyria-3-pro-preview",
                    contents=prompt + " Instrumental only, no vocals.",
                    config=types.GenerateContentConfig(
                        response_modalities=["AUDIO", "TEXT"],
                        # response_mime_type="audio/wav",
                    ),
                )

                if response.parts is None:
                    finish_reason = response.candidates[0].finish_reason if response.candidates else "unknown"
                    print(f"\n[WARN] No parts in response for prompt: '{prompt}' (attempt {attempt}/{max_retries})")
                    print(f"       Finish reason: {finish_reason}")
                    # Don't retry on content filter blocks — they won't change
                    if finish_reason in ("BLOCKLIST", "SAFETY", "RECITATION"):
                        break
                    time.sleep(2 ** attempt)  # exponential backoff: 2s, 4s, 8s
                    continue

                for part in response.parts:
                    if part.inline_data is not None:
                        audio_data = part.inline_data.data
                        if isinstance(audio_data, str):
                            audio_data = base64.b64decode(audio_data)
                        with open(audio_save_paths[i], "wb") as f:
                            f.write(audio_data)
                        break
                else:
                    print(f"\n[WARN] No audio data in response for prompt: '{prompt}'")
                break  # Success — exit retry loop

            except Exception as e:
                print(f"\n[ERROR] Attempt {attempt}/{max_retries} failed for prompt: '{prompt}' — {e}")
                if attempt < max_retries:
                    time.sleep(2 ** attempt)  # exponential backoff: 2s, 4s, 8s
                else:
                    print(f"[FAIL] Giving up on prompt: '{prompt}' after {max_retries} attempts")


if __name__ == "__main__":
    prompt_path = "/workspace/synthetic_data/prompt_manifest.jsonl"
    audio_dir_path = "/workspace/google_lyria_v3/data"
    manifest_dir_path = "/workspace/synthetic_data"
    batch_size = 8

    # Load client
    client = genai.Client()

    # Load data
    with open(prompt_path, 'r') as f:
        data = [json.loads(line) for line in f]

    # Unique instruments
    instruments = list(set([prompt['instrument'] for prompt in data]))

    # Check and create audio dirs
    for instrument in instruments:
        os.makedirs(f"{audio_dir_path}/{instrument}", exist_ok=True)

    # Optional: filter data on instrument
    selected_instruments = ["Oud"]
    data = [line for line in data if line['instrument'] in selected_instruments]

    # Create batches
    prompts_batches = [data[i:i+batch_size] for i in range(0, len(data), batch_size)]

    # Generate audios
    manifest = []
    for batch in tqdm(prompts_batches):
        prompts = [line['prompt'] for line in batch]
        audio_save_paths = []

        for i, line in enumerate(batch):
            audio_save_path = f"{audio_dir_path}/{line['instrument']}/{line['uttid']}.wav"
            audio_save_paths.append(audio_save_path)
            line['audio'] = audio_save_path
            manifest.append(line)

        create_synthetic_data(prompts, client, audio_save_paths)

    # Save manifest
    assert len(manifest) == len(data)
    with open(f"{manifest_dir_path}/lyria_manifest.jsonl", 'a') as f:
        f.writelines([json.dumps(line) + '\n' for line in manifest])
        