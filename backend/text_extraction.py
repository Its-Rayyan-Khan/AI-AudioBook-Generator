import io
from typing import List, Tuple

import PyPDF2
import pdfplumber
from docx import Document


def _extract_text_from_pdf_pypdf2(file_bytes: bytes) -> str:
	reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
	texts: List[str] = []
	for page in reader.pages:
		try:
			texts.append(page.extract_text() or "")
		except Exception:
			continue
	return "\n".join(texts)


def _extract_text_from_pdf_pdfplumber(file_bytes: bytes) -> str:
	texts: List[str] = []
	with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
		for page in pdf.pages:
			try:
				texts.append(page.extract_text() or "")
			except Exception:
				continue
	return "\n".join(texts)


def extract_text_from_pdf(file_bytes: bytes) -> Tuple[str, str]:
	"""Return (text, engine_used). Tries multiple engines for robustness."""
	try:
		text = _extract_text_from_pdf_pdfplumber(file_bytes)
		if text.strip():
			return text, "pdfplumber"
	except Exception:
		pass
	# Fallback
	try:
		text = _extract_text_from_pdf_pypdf2(file_bytes)
		return text, "PyPDF2"
	except Exception:
		return "", "error"


def extract_text_from_docx(file_bytes: bytes) -> str:
	bio = io.BytesIO(file_bytes)
	doc = Document(bio)
	paragraphs = [p.text for p in doc.paragraphs if p.text]
	return "\n".join(paragraphs)


def extract_text_from_txt(file_bytes: bytes, encoding: str = "utf-8") -> str:
	try:
		return file_bytes.decode(encoding, errors="ignore")
	except Exception:
		return file_bytes.decode("utf-8", errors="ignore")


def chunk_text(text: str, max_chars: int = 3500) -> List[str]:
	"""
	Split text into chunks roughly under max_chars for LLM/TTS processing.
	"""
	if not text:
		return []
	chunks: List[str] = []
	current: List[str] = []
	current_len = 0
	for paragraph in text.splitlines():
		p = paragraph.strip()
		if not p:
			continue
		if current_len + len(p) + 1 > max_chars:
			if current:
				chunks.append("\n".join(current))
				current = []
				current_len = 0
		current.append(p)
		current_len += len(p) + 1
	if current:
		chunks.append("\n".join(current))
	return chunks

