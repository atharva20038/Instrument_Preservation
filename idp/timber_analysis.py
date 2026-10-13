import os
import argparse
import json

import librosa
import numpy as np
import torchaudio
from scipy.stats import wasserstein_distance

eps = 1e-8

# load audio
def load_audio(path, target_sr=16000):
    waveform, sr = torchaudio.load(path)
    
    # resample
    if sr != target_sr:
        resampler = torchaudio.transforms.Resample(sr, target_sr)
        waveform = resampler(waveform)
        sr = target_sr
    
    return waveform.squeeze().numpy(), sr

# sftf
def compute_stft(audio, sr, n_fft=1024, hop_length=160, win_length=400):
    S = librosa.stft(
        audio,
        n_fft=n_fft,
        hop_length=hop_length,
        win_length=win_length,
        window="hann"
    )
    magnitude = np.abs(S)
    return magnitude

def compute_framewise_hnr_from_mag(mag):
    harmonic = librosa.decompose.nn_filter(
        mag,
        aggregate=np.median,
        metric='cosine'
    )

    noise = np.maximum(mag - harmonic, eps)

    h_energy = np.sum(harmonic**2, axis=0)
    n_energy = np.sum(noise**2, axis=0)

    hnr = 10 * np.log10((h_energy + eps) / (n_energy + eps))

    return np.clip(hnr, -50, 50)

# compute features
def compute_features(audio, sr):
    hop_length = 160
    win_length = 400

    magnitude = compute_stft(audio, sr, hop_length=hop_length, win_length=win_length)

    # MFCC
    mfcc = librosa.feature.mfcc(
        y=audio,
        sr=sr,
        n_mfcc=13,
        hop_length=hop_length
    )

    # Spectral features
    centroid = librosa.feature.spectral_centroid(S=magnitude, sr=sr).squeeze()
    rolloff = librosa.feature.spectral_rolloff(S=magnitude, sr=sr, roll_percent=0.85).squeeze()

    # Spectral flux
    norm_mag = magnitude / (np.sum(magnitude, axis=0, keepdims=True) + 1e-8)
    flux = np.sqrt(np.sum(np.diff(norm_mag, axis=1)**2, axis=0))
    flux = np.concatenate([[0], flux])

    # Frame-wise HNR
    hnr = hnr = compute_framewise_hnr_from_mag(magnitude)

    return {
        "mfcc": mfcc,
        "centroid": centroid,
        "rolloff": rolloff,
        "flux": flux,
        "hnr": hnr
    }

def process_folder(folder):
    all_features = {
        "mfcc": [],
        "centroid": [],
        "rolloff": [],
        "flux": [],
        "hnr": []
    }

    for file in os.listdir(folder):
        if not file.endswith((".wav")):
            continue

        path = os.path.join(folder, file)
        print(f"Processing: {path}")

        audio, sr = load_audio(path)
        feats = compute_features(audio, sr)

        for key in all_features:
            all_features[key].append(feats[key])

    # concatenate across all files
    for key in all_features:
        if key == "mfcc":
            all_features[key] = np.concatenate(all_features[key], axis=1)
        else:
            all_features[key] = np.concatenate(all_features[key])

    return all_features

def process_manifest_real(manifest):
    all_features = {
        "mfcc": [],
        "centroid": [],
        "rolloff": [],
        "flux": [],
        "hnr": []
    }

    for file in manifest:
        path = file["segment_path"]
        print(f"Processing: {path}")

        audio, sr = load_audio(path)
        feats = compute_features(audio, sr)

        for key in all_features:
            all_features[key].append(feats[key])

    # concatenate across all files
    for key in all_features:
        if key == "mfcc":
            all_features[key] = np.concatenate(all_features[key], axis=1)
        else:
            all_features[key] = np.concatenate(all_features[key])

    return all_features

def process_manifest_gen(manifest):
    all_features = {
        "mfcc": [],
        "centroid": [],
        "rolloff": [],
        "flux": [],
        "hnr": []
    }

    for file in manifest:
        path = file["path"]
        print(f"Processing: {path}")

        audio, sr = load_audio(path)
        feats = compute_features(audio, sr)

        for key in all_features:
            all_features[key].append(feats[key])

    # concatenate across all files
    for key in all_features:
        if key == "mfcc":
            all_features[key] = np.concatenate(all_features[key], axis=1)
        else:
            all_features[key] = np.concatenate(all_features[key])

    return all_features

def to_hist(x, bins=100):
    hist, _ = np.histogram(x, bins=bins, density=True)
    return hist

def compare_feature_sets(real, gen):
    results = {}

    # MFCC (dimension-wise)
    mfcc_dist = []
    for i in range(real["mfcc"].shape[0]):
        # Pass raw arrays directly
        mfcc_dist.append(wasserstein_distance(real["mfcc"][i], gen["mfcc"][i]))
        
    results["mfcc"] = np.mean(mfcc_dist)

    # Scalar features
    for key in ["centroid", "rolloff", "flux", "hnr"]:
        # Pass raw arrays directly
        results[key] = wasserstein_distance(real[key], gen[key])

    # # (See note below about why this overall score is problematic)
    # results["overall"] = np.mean(list(results.values()))

    return results

def evaluate(real_feats, gen_feats):
    print("--- Comparing ---")
    results = compare_feature_sets(real_feats, gen_feats)

    print("--- Results ---")
    for k, v in results.items():
        print(f"{k}: {v:.4f}")

    return results

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

    instruments = list(set([x["instrument"] for x in real_manifest]))
    print(instruments)

    # set seed
    np.random.seed(43)
    metrics = {}

    for instrument in instruments:
        real_manifest_instrument = [x for x in real_manifest if x["instrument"] == instrument]
        gen_manifest_instrument = [x for x in gen_manifest if x["instrument"] == instrument]

        # randomly sample min(len(real_manifest), len(gen_manifest)) samples
        min_len = min(len(real_manifest_instrument), len(gen_manifest_instrument), 128)
        print(f"Sampling {min_len} samples from both manifests")
        
        real_manifest_instrument = np.random.choice(real_manifest_instrument, min_len, replace=False)
        gen_manifest_instrument = np.random.choice(gen_manifest_instrument, min_len, replace=False)

        # Process real data
        real_feats = process_manifest_real(real_manifest_instrument)

        # Process generated data
        gen_feats = process_manifest_gen(gen_manifest_instrument)

        # Get metrics
        metrics[instrument] = evaluate(real_feats, gen_feats)

    # Save metrics into a JSON file
    with open(args.output_file, "w") as f:
        json.dump(metrics, f, indent=4)
    print(f"\nResults saved to {args.output_file}")