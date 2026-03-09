# A Multimodal AI-Powered Hybrid Approach to Document Parsing

A Python-based multimodal document parsing system that extracts structured data from **PDF, DOCX, TXT, images, audio, and video files**. The pipeline leverages **PPStructureV3** for OCR and document layout parsing, and **Llama** (via `llama-cpp-python`) for generating structured JSON output.

---

## 🚀 Features

- 🧩 **Multimodal Input Support**  
  Handles PDFs, DOCX, plain text, images, audio, and video.

- 📄 **PDF/Document Parsing**  
  Extracts text, tables, and images from documents.

- 🔍 **OCR for Images**  
  Uses PPStructureV3 to extract structured content from scanned documents or images.

- 🤖 **LLM Integration**  
  Llama3 converts parsed content into structured JSON.

- 🎤**Efficient Audio Transcribing along with Speaker Diarization**
  Audio files are efficiently parsed using whisper, resemblyzer and Agglomerative Clustering.

- 🎥**Implemented Effective Video Parsing Pipeline**
  An efficient video parsing pipeline has been implemented to extract structured JSON output from video files.
  
- ⚡ **Singleton Model Loading**  
  LLM, OCR and Whisper models are loaded only once for maximum efficiency.

- 🛡️ **Safe Loading**  
  Gracefully handles unsupported file types or corrupted files.

- ⏱️ **Timestamped JSON Output**  
  Automatically saves outputs with timestamps to avoid filename collisions.

---

## 📁 Directory Structure
```bash
Document_Parsing
├── app
│   ├── user_uploads               # Uploaded files
│   ├── final_json_output          # Final JSON results
│   ├── models
│   │   ├── llama3.gguf
│   │   ├── model_registry.py      # Singleton loaders for LLM and PPStructure
│   ├── pipelines
│   │   ├── text_pipeline_folder
│   │   │   ├── DocumentBlock.py
│   │   │   ├── file_router.py
│   │   │   ├── loaders.py
│   │   │   ├── generate_JSON.py
│   │   │   ├── pdf_images
│   │   │   ├── docx2pdf
│   │   ├── text_pipeline.py
│   │   ├── image_pipeline.py
│   │   └── output
│   └── __main__.py
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

1. **Clone the repository**:

```bash
git clone <your-repo-url>
cd multimodal_document_parsing
```

2. **Install dependencies**:

```bash
pip install -r requirements.txt
```

> **Note:**  
> - **PaddlePaddle** requires the extra index URL as specified in `requirements.txt`.  
> - **Llama.cpp** backend requires a C++ compiler. On Windows, install **Visual Studio with C++ build tools**. On Linux/macOS, ensure `g++` or `clang++` is installed.  
> - **docx2pdf** requires **Microsoft Word** to be installed, as it uses Word for conversion.

3. **Download the Llama3 model**:

Make sure the model is saved in the app/models directory as llama3.gguf:

```bash
mkdir -p app/models
curl -L -C - -o "app/models/llama3.gguf" "https://huggingface.co/QuantFactory/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf"
```

---

## 🏃 Usage

Run the application using:

```bash
python -m app
```

> **Note:** The main processing logic is handled in `__main__.py`. Simply provide the path to your file in the user_uploads folder. The script will automatically detect the file type (text, PDF, or image) based on the extension and route it to the appropriate processing pipeline. JSON output will be saved in final_json_output with a timestamped filename.

---

## 🌟 Future Improvements
- Improve LLM prompts for more robust JSON extraction.
- Add interactive GUI or web interface for easier file uploads and result previews.
