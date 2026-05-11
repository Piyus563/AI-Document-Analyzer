"""
doc_corrector.py
Generates a corrected version of the uploaded DOCX file.
"""

import io
import docx
import re
from .ai_analyzer import COMMON_MISSPELLINGS
import language_tool_python

# Initialize Grammar Checker
try:
    tool = language_tool_python.LanguageTool('en-US')
except Exception:
    tool = None

def correct_docx(file_bytes: bytes) -> bytes:
    """
    Reads a DOCX file, applies spelling and grammar corrections,
    and returns the corrected file as bytes, preserving the original design.
    """
    # Create document object from bytes
    doc = docx.Document(io.BytesIO(file_bytes))
    
    # Iterate through all paragraphs and runs
    for para in doc.paragraphs:
        for run in para.runs:
            if not run.text.strip():
                continue
            
            # Simple text replacement for common misspellings
            original_text = run.text
            new_text = original_text
            
            # Find all words in the run text
            words_in_text = set(re.findall(r'\b[a-zA-Z]+\b', new_text))
            for w in words_in_text:
                lower_w = w.lower()
                if lower_w in COMMON_MISSPELLINGS:
                    correction = COMMON_MISSPELLINGS[lower_w]
                    # Preserve capitalization (roughly)
                    if w.istitle():
                        correction = correction.title()
                    elif w.isupper():
                        correction = correction.upper()
                        
                    # Replace using word boundary
                    pattern = r'\b' + re.escape(w) + r'\b'
                    new_text = re.sub(pattern, correction, new_text)
            
            # Apply grammar correction using language-tool-python
            if tool and new_text.strip():
                try:
                    new_text = tool.correct(new_text)
                except Exception:
                    pass # Fallback to just spell correction if it fails
            
            if new_text != original_text:
                run.text = new_text

    # Save to buffer
    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()
