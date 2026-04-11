from __future__ import annotations


def parse_uploaded_file(uploaded_file) -> str:
    """Parse an uploaded file and return its text content.

    Supports: .md, .txt, .pdf, .docx, .doc, .csv
    Returns extracted text or an error message.
    """
    if uploaded_file is None:
        return ""

    name = uploaded_file.name.lower()

    try:
        if name.endswith((".md", ".txt", ".csv", ".json", ".yaml", ".yml")):
            return uploaded_file.read().decode("utf-8", errors="replace")

        elif name.endswith(".pdf"):
            return _parse_pdf(uploaded_file)

        elif name.endswith((".docx", ".doc")):
            return _parse_docx(uploaded_file)

        else:
            return f"[Unsupported file type: {name}. Supported: .md, .txt, .pdf, .docx, .csv]"

    except Exception as e:
        return f"[Error reading {name}: {str(e)}]"


def _parse_pdf(uploaded_file) -> str:
    """Extract text from a PDF file."""
    try:
        import io
        # Try PyPDF2 first (lighter)
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(io.BytesIO(uploaded_file.read()))
            text = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
            return "\n\n".join(text) if text else "[PDF contained no extractable text]"
        except ImportError:
            pass

        # Fallback: try pdfplumber
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(uploaded_file.read())) as pdf:
                text = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)
                return "\n\n".join(text) if text else "[PDF contained no extractable text]"
        except ImportError:
            pass

        return "[PDF parsing requires PyPDF2 or pdfplumber. Install with: pip install PyPDF2]"

    except Exception as e:
        return f"[Error parsing PDF: {str(e)}]"


def _parse_docx(uploaded_file) -> str:
    """Extract text from a DOCX file."""
    try:
        import io
        from docx import Document
        doc = Document(io.BytesIO(uploaded_file.read()))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n\n".join(paragraphs) if paragraphs else "[Document contained no text]"
    except ImportError:
        return "[DOCX parsing requires python-docx]"
    except Exception as e:
        return f"[Error parsing DOCX: {str(e)}]"


def get_supported_types() -> list:
    """Return list of supported file extensions for the uploader."""
    return ["md", "txt", "pdf", "docx", "doc", "csv", "json", "yaml", "yml"]
