import os
from .loaders import *
import logging

logging.basicConfig(level=logging.INFO)

def safe_load(file_path):
    """
    Load a file safely, returning blocks.
    Handles unsupported files and corrupted files gracefully.
    """
    ext = os.path.splitext(file_path)[1].lower()

    try:
        if ext == ".pdf":
            return load_pdf(file_path)
        elif ext in [".txt", ".md", ".log"]:
            return load_text(file_path)
        elif ext == ".docx":
            pdf_path = convert_docx_to_pdf(str(file_path))
            if pdf_path:
                return load_pdf(str(pdf_path))
            else:
                logging.error("Conversion failed.")
                return []
            #return load_docx(file_path)
        else:
            logging.warning(f"Unsupported file type: {ext}")
            return []  # Return empty list instead of raising
    except Exception as e:
        logging.error(f"Failed to load '{file_path}': {e}")
        return []  # Return empty list if file is corrupted/unreadable