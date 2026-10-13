import os
import json
import torch
import soundfile as sf
from tqdm import tqdm
from mustango import Mustango

device = "cuda" if torch.cuda.is_available() else "cpu"  # device

def create_synthetic_data(prompts, model, audio_save_paths):
    for i, prompt in enumerate(prompts):
        # generate (mustango handles inference internally)
        with torch.no_grad():
            music = model.generate(prompt)

        sf.write(
            audio_save_paths[i],
            music,
            samplerate=16000
        )

if __name__ == "__main__":
    prompt_path = "/workspace/synthetic_data/prompt_manifest.jsonl"
    audio_dir_path = "/workspace/mustango/data"
    manifest_dir_path = "/workspace/synthetic_data"
    batch_size = 8

    # load model
    model = Mustango("declare-lab/mustango")

    # load data
    with open(prompt_path, 'r') as f:
        data = [json.loads(line) for line in f]

    # unique instruments
    instruments = list(set([prompt['instrument'] for prompt in data]))

    # check and create audio dirs
    for instrument in instruments:
        os.makedirs(f"{audio_dir_path}/{instrument}", exist_ok=True)

    # Optional: filter data on instrument
    selected_instruments = ["Oud"]
    data = [line for line in data if line['instrument'] in selected_instruments]

    # create batches
    prompts_batches = [data[i:i+batch_size] for i in range(0, len(data), batch_size)]

    # generate audios
    manifest = []
    for batch in tqdm(prompts_batches):
        # extract prompts
        prompts = [line['prompt'] for line in batch]
        audio_save_paths = []

        # add records with audio save path to manifest
        for i, line in enumerate(batch):
            audio_save_path = f"{audio_dir_path}/{line['instrument']}/{line['uttid']}.wav"
            audio_save_paths.append(audio_save_path)
            line['audio'] = audio_save_path
            manifest.append(line)

        # save audios
        create_synthetic_data(prompts, model, audio_save_paths)

    # create manifest.jsonl
    assert len(manifest) == len(data)
    with open(f"{manifest_dir_path}/mustango_manifest.jsonl", 'a') as f:
        f.writelines([json.dumps(line) + '\n' for line in manifest])