import os
import io
import pdfplumber
import docx
from typing import List, BinaryIO
from backend.models.schemas import ExtractedText
from backend.utils.logger import log_pipeline_stage

@log_pipeline_stage("Extract PDF")
def extract_pdf(file_stream: BinaryIO) -> List[ExtractedText]:
    extracted = []
    with pdfplumber.open(file_stream) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if text:
                extracted.append(
                    ExtractedText(
                        text=text.strip(),
                        page_number=page_num,
                        section_heading=None,
                        file_type="pdf"
                    )
                )
    return extracted

@log_pipeline_stage("Extract DOCX")
def extract_docx(file_stream: BinaryIO) -> List[ExtractedText]:
    extracted = []
    doc = docx.Document(file_stream)
    
    current_heading = None
    current_text_block = []
    
    def flush_block():
        if current_text_block:
            joined_text = "\n".join(current_text_block).strip()
            if joined_text:
                extracted.append(
                    ExtractedText(
                        text=joined_text,
                        page_number=None,
                        section_heading=current_heading,
                        file_type="docx"
                    )
                )
            current_text_block.clear()

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
            
        style_name = para.style.name if para.style else ""
        if style_name.startswith("Heading"):
            # Flush previous block when encountering a new heading
            flush_block()
            current_heading = text
            # We can optionally include the heading itself as text
            current_text_block.append(text)
        else:
            current_text_block.append(text)
            
    # Flush remaining text
    flush_block()
    
    return extracted

@log_pipeline_stage("Extract TXT")
def extract_txt(file_stream: BinaryIO) -> List[ExtractedText]:
    extracted = []
    text_content = file_stream.read().decode('utf-8')
    
    # Split by double newline to approximate paragraphs
    paragraphs = text_content.split('\n\n')
    current_line = 1
    
    for para in paragraphs:
        clean_para = para.strip()
        line_count = para.count('\n') + 1
        
        if clean_para:
            extracted.append(
                ExtractedText(
                    text=clean_para,
                    page_number=current_line, # Using page_number to store line start
                    section_heading=None,
                    file_type="txt"
                )
            )
        current_line += line_count + 1 # +1 for the double newline
        
    return extracted

@log_pipeline_stage("Document Extraction")
def extract_document(file_stream: BinaryIO, filename: str) -> List[ExtractedText]:
    """Routes the file to the appropriate extractor based on extension."""
    ext = os.path.splitext(filename.lower())[1]
    
    if ext == '.pdf':
        return extract_pdf(file_stream)
    elif ext == '.docx':
        return extract_docx(file_stream)
    elif ext == '.txt':
        return extract_txt(file_stream)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
