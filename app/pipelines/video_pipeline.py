import os
import shutil
from pathlib import Path

from .video_pipeline_folder.audio_extractor import extract_audio
from .video_pipeline_folder.frame_extractor import extract_frames
from .audio_pipeline import run_audio_pipeline
from .image_pipeline import run_image_pipeline
import logging

logging.basicConfig(level=logging.INFO)

def run_video_pipeline(video_path):

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    audio_temp_output = "temp_audio.wav"
    base_dir = Path(__file__).resolve().parent
    video_pipeline_folder = os.path.join(base_dir, "video_pipeline_folder")
    audio_output = os.path.join(video_pipeline_folder,audio_temp_output)
    frames_folder = "frames"
    frames_folder_path = os.path.join(video_pipeline_folder,frames_folder)

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
        for frame_id, frame_path in enumerate(frames):
            result = run_image_pipeline(frame_path)
            parsed_doc.append({
                 "frame": f"Frame {frame_id+1}",
                    "structured_output": result.get("structured_image_output", {}),
                    "ocr_confidence": result.get("ocr_confidence", 0)
            })
        

        return {
            "audio_content": transcript_path,
            "total_frames": len(frames),
            "parsed_frames": parsed_doc
        }

    except Exception as e:
        logging.error(f"Failed: {e}")
        return []
    finally:
        if os.path.exists(audio_output):
            os.remove(audio_output)
        if os.path.exists(frames_folder_path):
            shutil.rmtree(frames_folder_path)

