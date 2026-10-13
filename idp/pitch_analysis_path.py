import os
import sys
import argparse
import json

import numpy as np
import torch
import torchaudio
import librosa
import crepe

import matplotlib.pyplot as plt

from scipy.stats import wasserstein_distance, entropy

def load_audio(path, target_sr=16000):
    waveform, sr = torchaudio.load(path)
    
    # resample
    if sr != target_sr:
        resampler = torchaudio.transforms.Resample(sr, target_sr)
        waveform = resampler(waveform)
        sr = target_sr
    
    return waveform.squeeze().numpy(), sr


# CREPE
def compute_crepe_f0(audio, sr, remove_zeros=False, hop_length=160):
    """
    hop_length: 160 @16kHz = 10 ms frames
    """
    time, frequency, confidence, _ = crepe.predict(
        audio,
        sr,
        step_size=1000 * hop_length / sr,  # in ms
        viterbi=True
    )
    
    f0 = frequency
    f0[confidence < 0.5] = 0  # remove low-confidence frames

    if remove_zeros:
        f0 = f0[f0 > 0]
    
    return f0


# PYIN
def compute_pyin_f0(audio, sr, remove_zeros=False, hop_length=160):
    f0, voiced_flag, voiced_prob = librosa.pyin(
        audio,
        fmin=librosa.note_to_hz('C2'),
        fmax=librosa.note_to_hz('C7'),
        sr=sr,
        hop_length=hop_length
    )
    
    # replace NaNs with 0
    f0 = np.nan_to_num(f0)

    if remove_zeros:
        f0 = f0[f0 > 0]
    
    return f0


# Delta F0 
def compute_delta_f0(f0):
    if len(f0) == 0:
        return np.array([])
    delta = np.diff(f0, prepend=f0[0])
    return delta


# full pipeline
def extract_pitch_features(audio_path, remove_zeros=False):
    audio, sr = load_audio(audio_path)

    crepe_f0 = compute_crepe_f0(audio, sr, remove_zeros)
    pyin_f0 = compute_pyin_f0(audio, sr, remove_zeros)

    crepe_df0 = compute_delta_f0(crepe_f0)
    pyin_df0 = compute_delta_f0(pyin_f0)

    return {
        "crepe_f0": crepe_f0,
        "pyin_f0": pyin_f0,
        "crepe_delta_f0": crepe_df0,
        "pyin_delta_f0": pyin_df0,
    }

def collect_features(file_list):
    all_crepe_f0, all_crepe_df0 = [], []
    all_pyin_f0, all_pyin_df0 = [], []

    for path in file_list:
        feats = extract_pitch_features(path, remove_zeros=True)

        # Skip this file if no pitch was detected by either algorithm
        if len(feats["crepe_f0"]) == 0 or len(feats["pyin_f0"]) == 0:
            print(f"Warning: No pitch detected in {path}. Skipping.")
            continue

        # use either crepe or pyin consistently
        crepe_f0 = feats["crepe_f0"]
        pyin_f0 = feats["pyin_f0"]

        crepe_df0 = feats["crepe_delta_f0"]
        pyin_df0 = feats["pyin_delta_f0"]

        all_crepe_f0.append(crepe_f0)
        all_crepe_df0.append(crepe_df0)

        all_pyin_f0.append(pyin_f0)
        all_pyin_df0.append(pyin_df0)

    # concatenate across all files
    all_crepe_f0 = np.concatenate(all_crepe_f0)
    all_crepe_df0 = np.concatenate(all_crepe_df0)

    all_pyin_f0 = np.concatenate(all_pyin_f0)
    all_pyin_df0 = np.concatenate(all_pyin_df0)

    return all_crepe_f0, all_crepe_df0, all_pyin_f0, all_pyin_df0

def compute_histogram(data, bins=100, range=None):
    hist, bin_edges = np.histogram(
        data,
        bins=bins,
        range=range,
        density=True
    )
    return hist, bin_edges

def convert_to_histogram(f0, df0):
    f0_range = (50, 2000)     # Hz
    df0_range = (-200, 200)   # Hz/frame

    f0_hist, _ = compute_histogram(f0, range=f0_range)
    df0_hist, _ = compute_histogram(df0, range=df0_range)

    return f0_hist, df0_hist

def compute_wasserstein(x, y):
    return wasserstein_distance(x, y)

def compute_kl(p, q):
    eps = 1e-8
    return entropy(p + eps, q + eps)

def compute_js(p, q):
    m = 0.5 * (p + q)
    return 0.5 * (entropy(p, m) + entropy(q, m))


if __name__ == "__main__":
    # argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("--real_manifest", type=str, required=True)
    parser.add_argument("--gen_manifest", type=str, required=True)
    parser.add_argument("--output_file", type=str, required=True)

    args = parser.parse_args()

    # load manifests
    # example real manifest: {"uttid": "Guitar_0001", "source_audio": "/workspace/yt_data/guitar_channel/Mixed_coversongs.mp3", "instrument": "Guitar", "utt_path": "/workspace/idp/data_16k/raw/real/Guitar/Guitar_0001.wav", "segment_id": "Guitar_0001_utt_0001", "segment_path": "/workspace/idp/data_16k/segmented/real/Guitar/Guitar_0001_utt_0001.wav"}
    # example gen manifest: {"uttid": "Guitar_0000", "source_audio": "/workspace/suno_ai/data/Guitar/Guitar_0000.wav", "instrument": "Guitar", "prompt": "Create a solo musical performance on the Guitar in the Western Classical genre, using Ionian mode and 2/4 rhythm.", "utt_path": "/workspace/idp/data_16k/raw/suno/Guitar/Guitar_0000.wav", "segment_id": "Guitar_0000_utt_0001", "segment_path": "/workspace/idp/data_16k/segmented/suno/Guitar/Guitar_0000_utt_0001.wav"}
    real_manifest = []
    gen_manifest = []
    with open(args.real_manifest, "r") as f:
        for line in f:
            real_manifest.append(json.loads(line))
    with open(args.gen_manifest, "r") as f:
        for line in f:
            gen_manifest.append(json.loads(line))

    
    # set seed
    np.random.seed(42)
    metrics = {}

    # calculate instrument wise metrics
    instruments = list(set([x["instrument"] for x in real_manifest]))
    print(instruments)
    for instrument in instruments:
        real_manifest_instrument = [x for x in real_manifest if x["instrument"] == instrument]
        gen_manifest_instrument = [x for x in gen_manifest if x["instrument"] == instrument]

        # randomly sample min(len(real_manifest), len(gen_manifest)) samples
        min_len = min(len(real_manifest_instrument), len(gen_manifest_instrument), 64)
        print(f"Sampling {min_len} samples from both manifests")
        # set seed for reproducibility
        
        real_manifest_instrument = np.random.choice(real_manifest_instrument, min_len, replace=False)
        gen_manifest_instrument = np.random.choice(gen_manifest_instrument, min_len, replace=False)
        
        # load features
        print("Loading real features...")
        real_crepe_f0, real_crepe_df0, real_pyin_f0, real_pyin_df0 = collect_features(
            [x["segment_path"] for x in real_manifest_instrument]
        )
        print("Loading gen features...")
        gen_crepe_f0, gen_crepe_df0, gen_pyin_f0, gen_pyin_df0 = collect_features(
            [x["path"] for x in gen_manifest_instrument]
        )

        # compute histograms (pyin)
        print("Computing real histograms (pyin)...")
        real_f0_hist_pyin, real_df0_hist_pyin = convert_to_histogram(
            real_pyin_f0, real_pyin_df0
        )
        print("Computing gen histograms (pyin)...")
        gen_f0_hist_pyin, gen_df0_hist_pyin = convert_to_histogram(
            gen_pyin_f0, gen_pyin_df0
        )

        # compute histograms (crepe)
        print("Computing real histograms (crepe)...")
        real_f0_hist_crepe, real_df0_hist_crepe = convert_to_histogram(
            real_crepe_f0, real_crepe_df0
        )
        print("Computing gen histograms (crepe)...")
        gen_f0_hist_crepe, gen_df0_hist_crepe = convert_to_histogram(
            gen_crepe_f0, gen_crepe_df0
        )

        # compute metrics
        metrics[instrument] = {
            "wasserstein_f0_pyin": compute_wasserstein(real_f0_hist_pyin, gen_f0_hist_pyin),
            "wasserstein_df0_pyin": compute_wasserstein(real_df0_hist_pyin, gen_df0_hist_pyin),
            "kl_f0_pyin": compute_kl(real_f0_hist_pyin, gen_f0_hist_pyin),
            "kl_df0_pyin": compute_kl(real_df0_hist_pyin, gen_df0_hist_pyin),
            "js_f0_pyin": compute_js(real_f0_hist_pyin, gen_f0_hist_pyin),
            "js_df0_pyin": compute_js(real_df0_hist_pyin, gen_df0_hist_pyin),
            "wasserstein_f0_crepe": compute_wasserstein(real_f0_hist_crepe, gen_f0_hist_crepe),
            "wasserstein_df0_crepe": compute_wasserstein(real_df0_hist_crepe, gen_df0_hist_crepe),
            "kl_f0_crepe": compute_kl(real_f0_hist_crepe, gen_f0_hist_crepe),
            "kl_df0_crepe": compute_kl(real_df0_hist_crepe, gen_df0_hist_crepe),
            "js_f0_crepe": compute_js(real_f0_hist_crepe, gen_f0_hist_crepe),
            "js_df0_crepe": compute_js(real_df0_hist_crepe, gen_df0_hist_crepe),
        }

    # save metrics
    with open(args.output_file, "w") as f:
        json.dump(metrics, f, indent=4)

    print("Metrics saved to:", args.output_file)
    