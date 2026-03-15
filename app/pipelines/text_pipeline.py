import os
import json
from pathlib import Path
from datetime import datetime
from .text_pipeline_folder.file_router import safe_load
from .text_pipeline_folder.generate_JSON import generate_blocks_json
from .text_pipeline_folder.DocumentBlock import DocumentBlock
import logging
import shutil

logging.basicConfig(level=logging.INFO)

def run_text_pipeline(text_file_path, base_dir="app/final_json_output"):
    """
    Complete pipeline for a single file:
    1. Load the file (PDF, DOCX, TXT, etc.) using safe_load
    2. Generate structured JSON for each DocumentBlock
    3. Save JSON output to a file if output path is provided
    """
    try:
        file_path = Path(text_file_path)
    
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
    
        logging.info(f"Loading file: {file_path}")
        blocks = safe_load(str(file_path))
    
        if not blocks:
            logging.warning(f"No blocks found in file: {file_path}")
            return []
    
        logging.info(f"Generating JSON for {len(blocks)} blocks")
        blocks_json = generate_blocks_json(blocks)
    
        return blocks_json

    except Exception as e:
        logging.exception(f"Unexpected error in text pipeline: {text_file_path}")
        raise RuntimeError(f"Unexpected error in text pipeline: {e}") from e

    finally:
        base_dir = Path(__file__).resolve().parent
        text_pipeline_folder = os.path.join(base_dir, "text_pipeline_folder")
        pdf_images_path = os.path.join(text_pipeline_folder, "pdf_images")
        docx_path = os.path.join(text_pipeline_folder, "docx2pdf")
    
        if os.path.exists(pdf_images_path):
            shutil.rmtree(pdf_images_path)
    
        if os.path.exists(docx_path):
            shutil.rmtree(docx_path)