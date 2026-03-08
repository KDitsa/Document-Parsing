import os
import shutil

from .video_pipeline_folder.audio_extractor import extract_audio
from .video_pipeline_folder.frame_extractor import extract_frames
from audio_pipeline import run_audio_pipeline
from image_pipeline import parse_document


def video_parsing_pipeline(video_path):

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    audio_output = "temp_audio.wav"
    frames_folder = "frames"

    try:
        audio_file = extract_audio(video_path, audio_output)
    
        frames = extract_frames(
            video_path,
            frames_folder,
            hist_threshold=0.75,      
            min_area_ratio=0.30,      # Only accept large changes
            check_interval=25        # Check every 25th frame
        )

        
        transcript_path = run_audio_pipeline(
            audio_file,
            enable_diarization=False
        )

        
        parsed_doc = []
        for frame_path in frames:
            result = parse_document(frame_path)
            parsed_doc.append({
                 "frame": frame_path,
                    "structured_output": result.get("structured_image_output", {}),
                    "ocr_confidence": result.get("ocr_confidence", 0)
            })
        

        return {
            "audio_file": transcript_path,
            "total_frames": len(frames),
            "parsed_frames": parsed_doc
        }

    
    finally:
        
            if os.path.exists(audio_output):
                os.remove(audio_output)
            if os.path.exists(frames_folder):
                shutil.rmtree(frames_folder)

