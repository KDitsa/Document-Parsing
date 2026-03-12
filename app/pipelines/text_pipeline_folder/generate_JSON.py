import json
from pathlib import Path
from tqdm import tqdm  # optional for progress bar
from ..image_pipeline import run_image_pipeline,_postprocess_llm_output
from ...models.model_registry import get_llm

def block_to_json(block):
    """
    Generate structured JSON from a single DocumentBlock.
    """
    # Convert block content to markdown-like text for clarity
    if block.type == "image":
        image_path = Path(block.content)
        markdown = run_image_pipeline(image_path)
        return markdown
    else:
        markdown = str(block.content)

    llm = get_llm()
    # Prepare LLM prompt
    prompt = f"""
    Extract structured data from this text and output valid JSON only.

    text:
    {markdown}
    
    Return valid JSON.
    """

    try:
        response = llm(
            prompt,
            max_tokens=800,
            temperature=0
        )
        llm_output = response["choices"][0]["text"].strip()
        return _postprocess_llm_output(llm_output)

    except Exception as e:
        return {"error": str(e)}
    

def generate_blocks_json(blocks):
    """
    Process a list of DocumentBlock objects and return JSON for each.
    """
    all_block_json = []
    for block in tqdm(blocks, desc="Processing blocks"):
        block_json = {
            "id": block.id,
            "type": block.type,
            "page_number": block.page_number,
            "bbox": block.bbox,
            "structured_content": block_to_json(block)
        }
        all_block_json.append(block_json)

    return all_block_json