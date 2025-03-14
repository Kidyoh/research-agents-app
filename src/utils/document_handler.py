import os
import tempfile
from typing import Dict, List, Optional
import PyPDF2
import docx2txt
import pandas as pd
import base64
from io import BytesIO

def process_uploaded_file(file) -> str:
    """
    Extract text content from an uploaded file.
    
    Args:
        file: The uploaded file object from Streamlit
        
    Returns:
        str: Extracted text content
    """
    # Create a temporary file to store the uploaded file
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.name)[1]) as tmp:
        tmp.write(file.getbuffer())
        tmp_path = tmp.name
    
    try:
        # Process based on file extension
        file_ext = os.path.splitext(file.name)[1].lower()
        
        if file_ext == '.pdf':
            return extract_text_from_pdf(tmp_path)
        elif file_ext == '.docx':
            return extract_text_from_docx(tmp_path)
        elif file_ext == '.txt':
            return extract_text_from_txt(tmp_path)
        elif file_ext == '.csv':
            return extract_text_from_csv(tmp_path)
        elif file_ext == '.xlsx':
            return extract_text_from_excel(tmp_path)
        else:
            return f"Unsupported file format: {file_ext}"
    finally:
        # Clean up the temporary file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file."""
    text = ""
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(file_path: str) -> str:
    """Extract text from a DOCX file."""
    return docx2txt.process(file_path)

def extract_text_from_txt(file_path: str) -> str:
    """Extract text from a text file."""
    with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
        return file.read()

def extract_text_from_csv(file_path: str) -> str:
    """Extract text from a CSV file."""
    df = pd.read_csv(file_path)
    return df.to_string()

def extract_text_from_excel(file_path: str) -> str:
    """Extract text from an Excel file."""
    df = pd.read_excel(file_path)
    return df.to_string()

def chunk_text(text, max_chunk_size=1000, overlap=100):
    """
    Split text into smaller chunks with overlap.
    
    Args:
        text: The text to chunk
        max_chunk_size: Maximum characters per chunk
        overlap: Number of characters to overlap between chunks
        
    Returns:
        List of text chunks
    """
    if not text:
        return []
    
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chunk_size
        chunks.append(text[start:end])
        start += max_chunk_size - overlap
    return chunks