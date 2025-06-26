from docx import Document as DocxDocument
import PyPDF2
import re


async def read_txt(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return remove_empty_lines(content)

async def read_docx(path):
    doc = DocxDocument(path)
    content = "\n".join(p.text for p in doc.paragraphs)
    return remove_empty_lines(content)

async def read_pdf(path):
    with open(path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        content = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    return remove_empty_lines(content)

    
def remove_empty_lines(text: str) -> str:
    return "\n".join(line for line in text.splitlines() if line.strip())

def markdown_bold_to_html(text):
    return re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)