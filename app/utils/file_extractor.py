from PyPDF2 import PdfReader
from docx import Document
from fastapi import HTTPException


def extract_text_from_file(file, file_extension):
    """
    Extract text from a file based on its extension.
    """
    if file_extension == "pdf":
        return extract_text_from_pdf(file)
    elif file_extension == "docx":
        return extract_text_from_docx(file)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type.")


def extract_text_from_pdf(file) -> str:
    """
    Extract text from a PDF file.
    """
    try:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"

        print(f"the text from the pdf file is: {text}\n\n")
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract text from PDF: {str(e)}")


def extract_text_from_docx(file) -> str:
    """
    Extract text from a DOCX file.
    """
    try:
        doc = Document(file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract text from DOCX: {str(e)}")
