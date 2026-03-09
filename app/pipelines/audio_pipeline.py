import os
import numpy as np
import pandas as pd
import whisper
import torch
from pydub import AudioSegment
from resemblyzer import preprocess_wav, VoiceEncoder
from sklearn.cluster import AgglomerativeClustering
from app.models.model_registry import get_whisper
from sklearn.preprocessing import normalize
from sklearn.metrics import silhouette_score
from datetime import timedelta
import logging
from pathlib import Path
import json

logging.basicConfig(level=logging.INFO)

CHUNK_LENGTH_MS = 30000
FRAME_DURATION = 1.5
MIN_SPEAKERS = 2
MAX_SPEAKERS = 5
WHISPER_MODEL = "tiny"

OUTPUT_DIR = "output"
CLEANUP_CHUNKS = True

model = get_whisper()
encoder = VoiceEncoder()

def sec_fmt(s):
    return str(timedelta(seconds=round(s, 3)))


def split_audio_to_chunks(path, chunk_length_ms):

    audio = AudioSegment.from_file(path)
    chunk_files = []

    for i in range(0, len(audio), chunk_length_ms):

        chunk = audio[i:i + chunk_length_ms]

        name = f"chunk_{i//chunk_length_ms}.wav"

        chunk.export(name, format="wav")

        chunk_files.append(name)

    return chunk_files


def embed_frames(frames):

    emb_list = []

    for f in frames:
        emb_list.append(encoder.embed_utterance(f))

    return np.vstack(emb_list)


def run_audio_pipeline(AUDIO_FILE, enable_diarization=False):

    if not os.path.exists(AUDIO_FILE):
        raise FileNotFoundError(f"Audio file not found: {AUDIO_FILE}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    chunks = split_audio_to_chunks(AUDIO_FILE, CHUNK_LENGTH_MS)

    rows = [] # For diarized output
    full_combined_text = "" # For non-diarized output (entire text)
    overall_confidence_sum = 0 # To accumulate avg_logprob for overall confidence
    overall_segment_count = 0 # To count total segments for overall confidence

    total_audio_duration_ms = 0
    try:
        audio = AudioSegment.from_file(AUDIO_FILE)
        total_audio_duration_ms = len(audio)
    except Exception as e:
        logging.warning(f"Could not determine total audio duration: {e}")

    for chunk_idx, chunk_fp in enumerate(chunks):

        print(f"\nProcessing chunk {chunk_idx}: {chunk_fp}")

        # Changed fp16 to True for reduced memory usage
        result = model.transcribe(chunk_fp, fp16=True, verbose=False)

        segments = result.get("segments", [])
        chunk_text = result.get("text", "").strip() # Text for the current chunk

        # Accumulate confidence scores for overall calculation
        for seg in segments:
            overall_confidence_sum += np.exp(seg.get("avg_logprob", -10))
            overall_segment_count += 1

        if not enable_diarization:
            full_combined_text += chunk_text + " " # Accumulate text

        else:

            wav = preprocess_wav(chunk_fp)

            sr = 16000
            frame_len = int(FRAME_DURATION * sr)

            frames = [
                wav[i:i + frame_len]
                for i in range(0, len(wav), frame_len)
                if len(wav[i:i + frame_len]) > 0
            ]

            if len(frames) == 0:
                continue

            embeddings = embed_frames(frames)

            embeddings = normalize(embeddings)

            best_k = MIN_SPEAKERS
            best_score = -1

            for k in range(MIN_SPEAKERS, min(MAX_SPEAKERS, len(frames)) + 1):

                try:

                    labels_test = AgglomerativeClustering(n_clusters=k).fit_predict(embeddings)

                    if len(set(labels_test)) < 2:
                        continue

                    score = silhouette_score(embeddings, labels_test)

                    if score > best_score:
                        best_score = score
                        best_k = k

                except:
                    continue

            clustering = AgglomerativeClustering(n_clusters=best_k)

            frame_labels = clustering.fit_predict(embeddings)

            chunk_offset = chunk_idx * (CHUNK_LENGTH_MS / 1000.0)

            for seg in segments:

                seg_start = seg["start"]
                seg_end = seg["end"]

                seg_mid = (seg_start + seg_end) / 2

                frame_idx = int(seg_mid // FRAME_DURATION)

                frame_idx = max(0, min(frame_idx, len(frame_labels) - 1))

                speaker = frame_labels[frame_idx]

                rows.append({

                    "start_time": sec_fmt(chunk_offset + seg_start),
                    "end_time": sec_fmt(chunk_offset + seg_end),
                    "speaker": f"Speaker_{speaker+1}",
                    "text": seg["text"].strip(),
                    "confidence": seg.get("avg_logprob", 0.0) 

                })


        if CLEANUP_CHUNKS:
            try:
                os.remove(chunk_fp)
            except:
                pass

    
    overall_confidence = overall_confidence_sum / overall_segment_count if overall_segment_count > 0 else 0.0

    if not enable_diarization:
        # Construct the single-entry output for non-diarized transcript
        single_entry_output = [{
            "start_time": "0:00:00.000",
            "end_time": sec_fmt(total_audio_duration_ms / 1000.0),
            "speaker": None,
            "text": full_combined_text.strip(),
            "overall_confidence": overall_confidence 
        }]
        print(f"\nNon-diarized transcript generated as variable.")
        return single_entry_output 

    # JSON OUTPUT for diarization enabled
    df = pd.DataFrame(rows)

    json_output_path = os.path.join(OUTPUT_DIR, "transcript_with_speakers.json")

    df.to_json(json_output_path, orient="records", indent=4)

    print(f"\nDiarized transcript saved \u2192 {json_output_path}")

    return json_output_path # Return the path to the JSON file
