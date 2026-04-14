from pathlib import Path
import shutil
import logging
import os
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"
import json

from .pipelines.text_pipeline import run_text_pipeline
from .pipelines.image_pipeline import run_image_pipeline
from .pipelines.audio_pipeline import run_audio_pipeline
from .pipelines.video_pipeline import run_video_pipeline 
from .braille import convert_to_braille

import magic
import time

def detect_mime(file_path: str):
    try:
        mime = magic.from_file(file_path, mime=True)
        return mime
    except Exception as e:
        return None

def process_file(test_file: str):
    start_time = time.time()
    result = {"success": False, "output_path": None, "error": None}
    mime = detect_mime(test_file)
    print(mime)
    if mime is None:
        result["error"] = "Could not determine file type"
        return result

    TEXT_MIME = {
        "application/pdf",
        "text/plain",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    }

    IMAGE_MIME = {
        "image/jpeg",
        "image/png"
    }

    AUDIO_MIME = {
        "audio/mpeg",      
        "audio/wav",
        "audio/x-wav",
        "audio/flac",
        "audio/mp4"
    }

    VIDEO_MIME = {
        "video/mp4",
        "video/quicktime",
        "video/x-matroska"
    }

    try:
        output_path = None
        
        if mime in TEXT_MIME:
            text_output = run_text_pipeline(test_file)
            try:
                if(text_output):
                    output_path = save_final_output(text_output, test_file)
            except RuntimeError as e:
                result["error"] = str(e)
            
        elif mime in IMAGE_MIME:
            image_output = run_image_pipeline(test_file)
            try:
                if(image_output):
                    output_path = save_final_output(image_output, test_file)
            except RuntimeError as e:
                result["error"] = str(e)
            
        elif mime in AUDIO_MIME:
            audio_output = run_audio_pipeline(test_file)
            try:
                if(audio_output):
                    output_path = save_final_output(audio_output, test_file)
            except RuntimeError as e:
                result["error"] = str(e)
            
        elif mime in VIDEO_MIME:
            video_output = run_video_pipeline(test_file)
            try:
                if(video_output):
                    output_path = save_final_output(video_output, test_file)
            except RuntimeError as e:
                result["error"] = str(e)

        else:
            result["error"] = f"Unsupported file type: {ext}"

        if output_path:
            result["success"] = True
            result["output_path"] = output_path
        else:
            if result["error"] is None:
                result["error"] = "Pipeline did not produce output"

    except Exception as e:
        logging.exception("Unexpected error")
        if result["error"] is None:
            result["error"] = str(e)
    finally:
        base_dir = Path(__file__).resolve().parent
        pipelines = os.path.join(base_dir, "pipelines")
        image_output = os.path.join(pipelines, "image_temp_output")
        audio_output = os.path.join(pipelines, "audio_temp_output")

        if os.path.exists(image_output):
            shutil.rmtree(image_output)
        if os.path.exists(audio_output):
            shutil.rmtree(audio_output)

    end_time = time.time()
    elapsed = end_time - start_time
    hours, rem = divmod(elapsed, 3600)
    minutes, seconds = divmod(rem, 60)
    print(f"Processing Time: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")
    return result

def save_final_output(result: dict, original_file: str, base_dir="app/final_json_output"):
    """
    Saves final structured output JSON.
    File naming:
    originalfilename.json

    Overwrite file content if exists
    """
    try:
        os.makedirs(base_dir, exist_ok=True)
    
        file_name = Path(original_file).stem
        output_file = Path(base_dir) / f"{file_name}.json"
    
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=4)
    
        logging.info(f"Saved JSON output to: {output_file}")
    
        return str(output_file)
    except Exception as e:
        logging.error(f"Failed to save '{output_file}': {e}")
        raise RuntimeError(f"Could not save final output: {e}")

if __name__ == "__main__":
    #test_file = r"..."# Give File Path
    #result = process_file(test_file)
    #logging.info(result)
    #convert_to_braille(r"...") # Give JSON File Path