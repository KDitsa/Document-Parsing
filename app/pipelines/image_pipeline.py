import os
import json
from pathlib import Path
from paddleocr import PPStructureV3
from llama_cpp import Llama
import re
from app.models.model_registry import get_ppstructure
from app.models.model_registry import get_llm
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)

def is_only_image_html(text: str) -> bool:
    # Looks for <img ...> anywhere
    pattern = r'<img\b[^>]*>'
    return bool(re.search(pattern, text, re.IGNORECASE))

def _run_ppstructure(image_path: str, output_dir: str) -> Path:
    """
    Runs PPStructureV3 on the image and saves markdown.
    Returns path to generated markdown file.
    """
    logging.info(image_path)
    image_path = str(Path(image_path))  # normalize path
    logging.info(image_path)

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"File not found: {image_path}")
        
    pipeline = get_ppstructure()
    output = pipeline.predict(image_path)

    md_path = None
    json_path = None

    for res in output:
        res.save_to_markdown(save_path=output_dir)
        res.save_to_json(save_path=output_dir)

        # Markdown filename logic
        image_name = Path(image_path).stem
        md_path = Path(output_dir) / f"{image_name}.md"
        json_path = Path(output_dir) / f"{image_name}_res.json"

    return md_path, json_path

def _calculate_ocr_confidence(json_path: Path) -> float:
    """
    Calculates OCR confidence from PPStructureV3 JSON output.
    Uses rec_scores and optionally rec_boxes for weighted scoring.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    ocr_data = data.get("overall_ocr_res", {})
    rec_scores = ocr_data.get("rec_scores", [])

    if not rec_scores:
        return 0.0

    avg_confidence = sum(rec_scores) / len(rec_scores)
    return round(avg_confidence, 4)

def _read_markdown(md_path: Path) -> str:
    """
    Reads markdown content from file.
    """
    with open(md_path, "r", encoding="utf-8") as f:
        return f.read()

def _call_llm(markdown_text: str) -> str:
    """
    Sends markdown text to Llama3 and returns raw output.
    """
    llm = get_llm()

    prompt = f"""
    Extract structured data from this document and return valid JSON only.
    
    text:
    {markdown_text}
    
    Return only JSON.
    """

    response = llm(
        prompt,
        max_tokens=800,
        temperature=0,
        stop=["</s>"]
    )

    return response["choices"][0]["text"].strip()

def _postprocess_llm_output(llm_output: str) -> dict:
    """
    Extracts and validates JSON from LLM output.
    Ensures output starts from { and ends at } only.
    Returns parsed Python dict.
    """
    match = re.search(r"\{.*\}", llm_output, re.DOTALL)
    
    if not match:
        raise ValueError("No valid JSON object found in LLM output.")

    json_str = match.group(0)

    try:
        parsed_json = json.loads(json_str)
    except json.JSONDecodeError as e:
        return json_str

    return parsed_json

def run_image_pipeline(image_path: str, output_dir: str = "image_temp_output"):
    """
    Full pipeline:
    Image -> PPStructureV3 -> Markdown -> LLM -> JSON output
    Also computes OCR confidence from JSON.
    """
    try:
        file_path = Path(image_path)
    
        if not file_path.exists():
            logging.error(f"File does not exist: {file_path}")
            return []
            
        base_dir = Path(__file__).resolve().parent
        output_dir = base_dir / output_dir
        output_dir.mkdir(exist_ok=True, parents=True)
        
        md_path, json_path = _run_ppstructure(image_path, output_dir)
        if(not md_path):
            logging.warning("Failed to Parse")
            return {
                "structured_image_output": null,
                "ocr_confidence": 0
            }
        
        # Calculate OCR confidence
        ocr_confidence = _calculate_ocr_confidence(json_path)
    
        markdown_text = _read_markdown(md_path)
        if(is_only_image_html(markdown_text) or not markdown_text):
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            structured_json =  data.get("parsing_res_list", {})
            return {
                "structured_image_output": structured_json,
                "ocr_confidence": ocr_confidence
            }
        llm_output = _call_llm(markdown_text)
        structured_json = _postprocess_llm_output(llm_output)
        if(not structured_json):
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            structured_json =  data.get("parsing_res_list", {})
        
        return {
            "structured_image_output": structured_json,
            "ocr_confidence": ocr_confidence
        }
    except Exception as e:
        logging.exception(f"Unexpected error in image pipeline: {text_file_path}")
        return {
            "structured_image_output": null,
            "ocr_confidence": 0
        }