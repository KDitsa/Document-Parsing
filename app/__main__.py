from .pipelines.text_pipeline import process_file
from .pipelines.image_pipeline import parse_document

if __name__ == "__main__":
    try:
        if ext == [".pdf",".txt", ".md", ".log",".docx"]:
            #test_file = r"..." # Give File Path
            #process_file(test_file)
        else if ext == [".jpg",".jpeg","png"]:
            #test_file = r"..." # Give File Path
            #output = parse_document(test_file)
            #save_final_output(output, test_file)
        else:
            logging.warning(f"Unsupported file type: {ext}")
            return []  # Return empty list instead of raising
    except Exception as e:
        logging.error(f"Failed to load '{file_path}': {e}")