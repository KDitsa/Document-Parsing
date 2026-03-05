import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)

_llm_model = None
_ppstructure = None
_whisper = None

def get_llm():
    """
    Singleton loader for LLM model.
    Loads only once.
    """
    global _llm_model

    if _llm_model is None:
        logging.info("Loading LLM model...")
        from llama_cpp import Llama
        model_path = Path(__file__).parent / "llama3.gguf"

        _llm_model = Llama(
            model_path=str(model_path),
            n_ctx=2048,
            n_threads=4
        )
        logging.info("LLM loaded successfully.")

    return _llm_model

def get_ppstructure():
    """
    Singleton loader for PPStructure model.
    Loads only once.
    """
    global _ppstructure

    if _ppstructure is None:
        logging.info("Loading PPStructure model...")
        from paddleocr import PPStructureV3
        _ppstructure = PPStructureV3(device="cpu")
        logging.info("PPStructure loaded.")

    return _ppstructure

def get_whisper():
    """
    Singleton loader for Whisper model.
    Loads only once.
    """
    global _whisper

    if _whisper is None:
        logging.info("Loading Whisper model...")
        import whisper
        model_size = "tiny"  
        _whisper = whisper.load_model(model_size)
        logging.info("Whisper model loaded.")
    return _whisper