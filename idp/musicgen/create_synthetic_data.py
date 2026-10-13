import os
import json
import torch
import scipy
from tqdm import tqdm
from transformers import AutoProcessor, MusicgenForConditionalGeneration

device = "cuda" if torch.cuda.is_available() else "cpu" # device

def create_synthetic_data(prompts, processor, model, audio_save_paths):
    inputs = processor(
        text=prompts,
        padding=True,
        return_tensors="pt",
    )

    # move inputs to GPU
    inputs = {k: v.to(device) for k, v in inputs.items()}

    # generate (no grad for inference)
    with torch.no_grad():
        audio_values = model.generate(**inputs, max_new_tokens=512)

    # move back to CPU before saving
    audio_values = audio_values.cpu()

    sampling_rate = model.config.audio_encoder.sampling_rate

    for i, audio_save_path in enumerate(audio_save_paths):
        scipy.io.wavfile.write(
            audio_save_path,
            rate=sampling_rate,
            data=audio_values[i, 0].numpy()
        )

if __name__ == "__main__":
    prompt_path  = "/workspace/synthetic_data/prompt_manifest.jsonl"
    audio_dir_path = "/workspace/musicgen/data"
    manifest_dir_path = "/workspace/synthetic_data"
    batch_size = 4

    # load model
    processor = AutoProcessor.from_pretrained("facebook/musicgen-large")
    model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-large").to(device)

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
        # extract propmts
        prompts = [line['prompt'] for line in batch]
        audio_save_paths = []

        # add records with audio save path to manifest
        for i, line in enumerate(batch):
            audio_save_path = f"{audio_dir_path}/{line['instrument']}/{line['uttid']}.wav"
            audio_save_paths.append(audio_save_path)
            line['audio'] = audio_save_path
            manifest.append(line)
        
        # save audios
        create_synthetic_data(prompts, processor, model, audio_save_paths)

    # create manifest.jsonl
    assert len(manifest) == len(data)
    with open(f"{manifest_dir_path}/musicgen_manifest.jsonl", 'a') as f:
        f.writelines([json.dumps(line) + '\n' for line in manifest])
        