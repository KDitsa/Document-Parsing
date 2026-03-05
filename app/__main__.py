from doc import ext

from .pipelines.text_pipeline import process_file
from .pipelines.image_pipeline import parse_document
from .pipelines.audio_pipeline import run_audio_pipeline

if __name__ == "__main__":
    try:
        if ext == [".pdf",".txt", ".md", ".log",".docx"]:
            #test_file = r"..." # Give File Path
            #process_file(test_file)
        elif ext == [".jpg",".jpeg","png"]:
            #test_file = r"..." # Give File Path
            #output = parse_document(test_file)
            #save_final_output(output, test_file)
        elif ext == [".mp3", ".wav", ".m4a"]:
            #test_file = r"..." # Give File Path
            #output = run_audio_pipeline(test_file, enable_diarization=True)
            #save_final_output(output, test_file)
        else:
            logging.warning(f"Unsupported file type: {ext}")
            return []  # Return empty list instead of raising
    except Exception as e:
        logging.error(f"Failed to load '{file_path}': {e}")