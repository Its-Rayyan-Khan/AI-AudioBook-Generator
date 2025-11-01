# 🎧 AI AudioBook Generator

Convert PDFs, DOCX, and TXT files into engaging audiobooks via a Streamlit web app.

## Features
- Upload multiple documents
- Extract text (PDF, DOCX, TXT)
- Optional LLM enrichment (OpenAI API or local fallback)
- Offline TTS using pyttsx3 (WAV/MP3 output)
- Download single audio or a ZIP for multiple files

## Requirements
- Python 3.10+
- Optional: `ffmpeg` in PATH for MP3 conversion (pydub)
- Optional: `OPENAI_API_KEY` environment variable for LLM enrichment

## Setup
```bash
python -m venv .venv
# Windows PowerShell
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If you want MP3 output and don't have ffmpeg, either install it or choose WAV in the sidebar.

## Run
```bash
streamlit run app.py
```
Open the printed local URL in your browser. Upload files, adjust settings in the sidebar, and click "Generate Audiobook".

## Environment Variables (optional)
- `OPENAI_API_KEY`: Enables OpenAI model for enrichment (default model `gpt-4o-mini`; set `OPENAI_MODEL` to override)
- `GEMINI_API_KEY`: Placeholder support; currently uses local fallback

## Notes
- On first run, pyttsx3 will use the system voices installed on Windows.
- If MP3 export fails, switch output format to WAV or install ffmpeg.

