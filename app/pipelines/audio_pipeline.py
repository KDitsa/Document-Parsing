from ..models.model_registry import get_whisper,get_voice_encoder
import torch
import numpy as np
import librosa
import whisper
from sklearn.cluster import SpectralClustering
from scipy.sparse.csgraph import laplacian
from sklearn.metrics import pairwise_distances

def sec_fmt(seconds):
    """Helper to format seconds into a clean string or float."""
    return round(seconds, 3)

def merge_segments(json_output):
    """
    Merges consecutive segments if they share the same speaker.
    """
    if not json_output:
        return []

    merged = []
    # Start with the first segment
    current_entry = json_output[0].copy()

    for next_seg in json_output[1:]:
        # If the speaker is the same, merge them
        if next_seg['speaker'] == current_entry['speaker']:
            current_entry['end_time'] = next_seg['end_time']
            # Join the text with a space
            current_entry['text'] += " " + next_seg['text']
            # Average the confidence (optional, but keeps it representative)
            current_entry['confidence'] = round((current_entry['confidence'] + next_seg['confidence']) / 2, 4)
        else:
            # If speaker changes, push the finished entry and start a new one
            merged.append(current_entry)
            current_entry = next_seg.copy()

    # Append the last remaining entry
    merged.append(current_entry)
    return merged

def estimate_speakers(embeddings, max_speakers=8):
    """
    Guesses the number of speakers using the Eigengap Heuristic.
    Looks for the largest 'jump' in eigenvalues to find the natural cluster count.
    """
    if len(embeddings) < 2:
        return 1
    
    # Calculate Affinity Matrix (Cosine Similarity)
    # Spectral clustering needs similarity (1 - distance)
    S = 1 - pairwise_distances(embeddings, metric='cosine')
    
    # Compute Normalized Laplacian
    L = laplacian(S, normed=True)
    eigenvalues, _ = np.linalg.eigh(L)
    
    # The Eigengap Heuristic: find the largest difference between consecutive eigenvalues
    # We skip the first eigenvalue as it's always 0
    gaps = np.diff(eigenvalues[:max_speakers + 1])
    
    # The index of the max gap + 1 gives us the estimated K
    num_speakers = np.argmax(gaps) + 1
    return max(1, num_speakers)

def get_stable_embedding(audio, sr, start, end):
    """Extracts and L2-normalizes speaker embeddings with safety checks."""
    start_samp, end_samp = int(start * sr), int(end * sr)
    signal = audio[start_samp:end_samp]
    
    if len(signal) < 1600 or np.max(np.abs(signal)) < 0.001: 
        return None
    classifier = get_voice_encoder()
    device = "cuda" if torch.cuda.is_available() else "cpu"

    with torch.no_grad():
        emb = classifier.encode_batch(torch.tensor(signal).unsqueeze(0).to(device)).cpu().numpy().flatten()
        
        # Check for NaN/Inf (happens with corrupted audio or pure silence)
        if np.any(np.isnan(emb)) or np.any(np.isinf(emb)):
            return None
            
        norm = np.linalg.norm(emb)
        if norm < 1e-6: return None 
        
        return emb / norm

def run_audio_pipeline(audio_path):
    print("--- Starting Pipeline ---")
    y, sr = librosa.load(audio_path, sr=16000)
    
    # Step 1: Transcribe
    print("Transcribing with Whisper Tiny...")
    whisper_model = get_whisper()
    result = whisper_model.transcribe(audio_path, beam_size=5)
    segments = result['segments'] 
    
    embeddings, valid_segs = [], []
    
    # Step 2: Extract Embeddings
    print(f"Extracting embeddings for {len(segments)} segments...")
    for i,seg in enumerate(segments):
        emb = get_stable_embedding(y, sr, seg['start'], seg['end'])
        if emb is not None:
            embeddings.append(emb)
            valid_segs.append(i)
    
    if not embeddings:
        print("No valid speech detected.")
        return

    X = np.array(embeddings)
    
    # Step 3: Auto-Guess Speaker Count
    print("Analyzing vocal patterns to estimate speaker count...")
    num_speakers = estimate_speakers(X)
    print(f"Detected Estimated Speakers: {num_speakers}")
    
    # Step 4: Spectral Clustering with Auto-K
    clusterer = SpectralClustering(
        n_clusters=num_speakers, 
        affinity='cosine', 
        assign_labels='cluster_qr', 
        random_state=42
    )
    labels = clusterer.fit_predict(X)
    speaker_map = {idx: labels[i] for i, idx in enumerate(valid_segs)}
    # Step 5: Final Output
    json_output = []
    chunk_offset = 0 # Usually 0 unless you are processing audio in manual chunks

    for i, seg in enumerate(segments):
        # Get the assigned speaker from our final_labels mapping
        speaker_val = speaker_map.get(i, 0)
        
        # Calculate confidence from logprob (Standard Whisper metric)
        # If avg_logprob is missing, we default to a low value
        logprob = seg.get("avg_logprob", -10)
        confidence = float(np.exp(seg.get("avg_logprob", -10)))        
        entry = {
            "start_time": sec_fmt(chunk_offset + seg['start']),
            "end_time": sec_fmt(chunk_offset + seg['end']),
            "speaker": f"Speaker_{speaker_val + 1}",
            "text": seg["text"].strip(),
            "confidence": round(confidence, 4)
        }
        json_output.append(entry)
        
    final_merged_output = merge_segments(json_output)
    
    return final_merged_output