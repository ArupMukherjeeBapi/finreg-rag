import json
from pathlib import Path
from pypdf import PdfReader

PDF_PATH = Path("data/raw/ssm-guide-2014.pdf")


def extract_pages(pdf_path: Path) -> list[dict]:
    reader = PdfReader(pdf_path)
    pages = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages.append({"page": page_number, "text": text})
    return pages


CHUNK_SIZE = 1000
OVERLAP = 150
OUT_PATH = Path("data/processed/chunks.jsonl")


def chunk_page(text: str, page: int) -> list[dict]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        piece = text[start:end].strip()
        if piece:
            chunks.append({"page": page, "start": start, "text": piece})
        start = end - OVERLAP
    return chunks


if __name__ == "__main__":
    pages = extract_pages(PDF_PATH)
    chunks = []
    for page in pages:
        chunks.extend(chunk_page(page["text"], page["page"]))

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as f:
        for chunk_id, chunk in enumerate(chunks):
            chunk["id"] = chunk_id
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    print(f"pages: {len(pages)}, chunks: {len(chunks)}")
    print(chunks[10])
