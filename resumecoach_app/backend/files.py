"""Extract text from uploaded PDF / DOCX / TXT files."""
import io


def read_file(name: str, data: bytes) -> str:
    name = name.lower()
    if len(data) > 5_000_000:
        raise ValueError("File too large (max 5 MB)")
    if name.endswith(".pdf"):
        from pypdf import PdfReader
        text = "\n".join(p.extract_text() or "" for p in PdfReader(io.BytesIO(data)).pages)
    elif name.endswith(".docx"):
        import docx
        text = "\n".join(p.text for p in docx.Document(io.BytesIO(data)).paragraphs)
    else:
        text = data.decode("utf-8", "ignore")
    if len(text.strip()) < 30:
        raise ValueError("No readable text found (scanned PDF?)")
    return text
