import os
import json
from pathlib import Path
from datetime import datetime
from .text_pipeline_folder.file_router import safe_load
from .text_pipeline_folder.generate_JSON import generate_blocks_json
from .text_pipeline_folder.DocumentBlock import DocumentBlock
import logging

logging.basicConfig(level=logging.INFO)

def process_file(text_file_path, base_dir="app/final_json_output"):
    """
    Complete pipeline for a single file:
    1. Load the file (PDF, DOCX, TXT, etc.) using safe_load
    2. Generate structured JSON for each DocumentBlock
    3. Save JSON output to a file if output path is provided
    """
    file_path = Path(text_file_path)

    if not file_path.exists():
        logging.error(f"File does not exist: {file_path}")
        return []

    logging.info(f"Loading file: {file_path}")
    blocks = safe_load(str(file_path))

    if not blocks:
        logging.warning(f"No blocks found in file: {file_path}")
        return []

    logging.info(f"Generating JSON for {len(blocks)} blocks")
    blocks_json = generate_blocks_json(blocks)

    file_name = Path(text_file_path).stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    output_file = Path(base_dir) / f"{file_name}_{timestamp}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(blocks_json, f, indent=2)
    logging.info(f"Saved JSON output to: {output_file}")

    return str(output_file)