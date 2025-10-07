import os
from typing import List
import fitz

def list_pdf_files(pdf_folder: str) -> List[str]:
    fnames = []
    for fname in os.listdir(pdf_folder):
        if fname.lower().endswith(".pdf"):
            fnames.append(os.path.join(pdf_folder, fname))
    return fnames

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract entire text from PDF as one string (naive)."""
    doc = fitz.open(pdf_path)
    pages = []
    for page in doc:
        text = page.get_text()
        pages.append(text)
    return "\n".join(pages)

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Split the text into overlapping chunks.
    chunk_size = maximum characters per chunk (or tokens).
    overlap = how many characters overlap between chunks.
    """
    chunks = []
    start = 0
    L = len(text)
    while start < L:
        end = min(start + chunk_size, L)
        chunk = text[start:end]
        chunks.append(chunk)
        if end == L:
            break
        start = end - overlap
    return chunks