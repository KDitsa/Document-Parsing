import os
import shutil
from pathlib import Path

from .video_pipeline_folder.audio_extractor import extract_audio
from .video_pipeline_folder.frame_extractor import extract_slides_chunked
from .audio_pipeline import run_audio_pipeline
from .image_pipeline import run_image_pipeline, _run_ppstructure
import logging
from difflib import SequenceMatcher

logging.basicConfig(level=logging.INFO)

def _get_first_two_lines(md_path: Path) -> str:
    try:
        with open(md_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return "".join(lines[:2]).strip()
    except:
        return ""

def similarity(a, b):
    if not a or not b:
        return 0.0

    # take smaller length
    min_len = min(len(a), len(b))

    # trim both to same size
    a_trim = a[:min_len]
    b_trim = b[:min_len]

    return SequenceMatcher(None, a_trim, b_trim).ratio()

def run_video_pipeline(video_path):

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    audio_temp_output = "temp_audio.wav"
    base_dir = Path(__file__).resolve().parent
    video_pipeline_folder = os.path.join(base_dir, "video_pipeline_folder")
    audio_output = os.path.join(video_pipeline_folder,audio_temp_output)
    frames_folder = "frames"
    frames_folder_path = os.path.join(video_pipeline_folder,frames_folder)
    transcript_path = ""

    try:
        audio_file = extract_audio(video_path, audio_output)
    
        frames = extract_slides_chunked(
            video_path,
            frames_folder
        )

        if os.path.exists(audio_file):
            transcript_path = run_audio_pipeline(audio_file)

        
        parsed_doc = []
        i = 0

        while i < len(frames):

            frame_path = frames[i]
            md_path, json_path = _run_ppstructure(frame_path, "image_temp_output")
            header_i = _get_first_two_lines(md_path)

            j = i + 1

            # move forward while headers match
            while j < len(frames):
                md_path_next, json_path_next = _run_ppstructure(frames[j], "image_temp_output")
                header_j = _get_first_two_lines(md_path_next)

                if similarity(header_i, header_j) >= 0.8:
                    j += 1
                else:
                    break

            # last matching frame
            valid_frame_index = j - 1
            # logging.info(f"Frame {valid_frame_index} is valid")
            valid_frame_path = frames[valid_frame_index]

            result = run_image_pipeline(valid_frame_path,"image_temp_output",True)

            parsed_doc.append({
                "frame": f"Frame {valid_frame_index+1}",
                "structured_output": result.get("structured_image_output", {}),
                "ocr_confidence": result.get("ocr_confidence", 0)
            })

            # jump to next new frame
            i = j
        

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

