import logging
from pathlib import Path
import torchaudio

if not hasattr(torchaudio, "set_audio_backend"):
    def dummy_backend(x): pass
    torchaudio.set_audio_backend = dummy_backend
    
logging.basicConfig(level=logging.INFO)

_llm_model = None
_ppstructure = None
_whisper = None
_encoder = None

def get_llm():
    """
    Singleton loader for LLM model.
    Loads only once.
    """
    global _llm_model

    if _llm_model is None:
        try:
            logging.info("Loading LLM model...")
            from llama_cpp import Llama
            model_path = Path(__file__).parent / "llama3.gguf"
    
            _llm_model = Llama(
                model_path=str(model_path),
                n_gpu_layers=-1,
                n_ctx=2048,
                n_threads=4
            )
            logging.info("LLM loaded successfully.")
        except Exception as e:
            logging.exception("Failed to load llama")
            raise RuntimeError(f"Could not load llama: {e}") from e

    return _llm_model

def get_ppstructure():
    """
    Singleton loader for PPStructure model.
    Loads only once.
    """
    global _ppstructure

    if _ppstructure is None:
        try:
            logging.info("Loading PPStructure model...")
            from paddleocr import PPStructureV3
            _ppstructure = PPStructureV3(device="cpu")
            logging.info("PPStructure loaded.")
        except Exception as e:
            logging.exception("Failed to load PPStructureV3")
            raise RuntimeError(f"Could not load PPStructureV3: {e}") from e

    return _ppstructure

def get_whisper():
    """
    Singleton loader for Whisper model.
    Loads only once.
    """
    global _whisper

    if _whisper is None:
        try:
            logging.info("Loading Whisper model...")
            import whisper
            model_size = "tiny"  
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
            _whisper = whisper.load_model(model_size, device=device)
            logging.info("Whisper model loaded.")
        except Exception as e:
            logging.exception("Failed to load Whisper")
            raise RuntimeError(f"Could not load Whisper: {e}") from e
        
    return _whisper

def get_voice_encoder():
    """
    Singleton loader for VoiceEncoder.
    Loads only once.
    """
    global _encoder

    if _encoder is None:
        try:
            logging.info("Loading VoiceEncoder...")
            from speechbrain.inference.speaker import EncoderClassifier
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
            _encoder = EncoderClassifier.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", run_opts={"device": device})
            logging.info("VoiceEncoder loaded.")
        except Exception as e:
            logging.exception("Failed to load VoiceEncoder")
            raise RuntimeError(f"Could not load VoiceEncoder: {e}") from e

    return _encoder