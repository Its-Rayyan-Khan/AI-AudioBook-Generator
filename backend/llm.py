import os
from typing import List, Optional

import requests
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()


def enrich_text_chunks(chunks: List[str]) -> List[str]:
	"""
	Rewrite text chunks for audiobook-style narration.
	If OPENAI_API_KEY or GEMINI_API_KEY is present, call the respective API; otherwise, apply a simple local heuristic.
	"""
	api_key_openai = os.getenv("OPENAI_API_KEY")
	api_key_gemini = os.getenv("GEMINI_API_KEY")
	model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

	if api_key_openai:
		return _enrich_with_openai(chunks, api_key_openai, model)
	if api_key_gemini:
		return _enrich_with_gemini(chunks, api_key_gemini)
	return [_local_enrich(c) for c in chunks]


def _local_enrich(text: str) -> str:
	# Lightweight formatting: ensure sentences end with punctuation; add brief intro phrase.
	s = text.strip()
	if not s:
		return s
	if not s.endswith((".", "!", "?")):
		s += "."
	return f"Narration:\n\n{s}"


def _enrich_with_openai(chunks: List[str], api_key: str, model: str) -> List[str]:
	url = "https://api.openai.com/v1/chat/completions"
	headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
	prompt = (
		"Rewrite the following text for an engaging audiobook narration style."
		" Keep structure and meaning, improve flow and clarity."
	)
	results: List[str] = []
	for c in chunks:
		payload = {
			"model": model,
			"messages": [
				{"role": "system", "content": "You are a skilled audiobook editor."},
				{"role": "user", "content": f"{prompt}\n\nText:\n{c}"},
			],
			"temperature": 0.5,
		}
		try:
			resp = requests.post(url, headers=headers, json=payload, timeout=90)
			resp.raise_for_status()
			data = resp.json()
			content = data["choices"][0]["message"]["content"].strip()
			results.append(content)
		except Exception:
			results.append(_local_enrich(c))
	return results


def _enrich_with_gemini(chunks: List[str], api_key: str) -> List[str]:
	"""Use Google Gemini to rewrite text for audiobook-style narration."""
	try:
		import google.generativeai as genai  # type: ignore
	except Exception:
		# SDK not installed; fallback locally
		return [_local_enrich(c) for c in chunks]

	genai.configure(api_key=api_key)
	model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
	prompt = (
		"Rewrite the following text for an engaging audiobook narration style. "
		"Keep structure and meaning, improve flow and clarity."
	)
	results: List[str] = []
	for c in chunks:
		try:
			model = genai.GenerativeModel(model_name)
			resp = model.generate_content(f"{prompt}\n\nText:\n{c}")
			text = getattr(resp, "text", None)
			if not text:
				# Some SDK versions return candidates
				cands = getattr(resp, "candidates", None)
				if cands and len(cands) > 0:
					text = getattr(cands[0], "content", None)
					if hasattr(text, "parts") and text.parts:
						text = "".join(getattr(p, "text", "") for p in text.parts)
			text = (text or "").strip()
			results.append(text if text else _local_enrich(c))
		except Exception:
			results.append(_local_enrich(c))
	return results

