import requests

def test_pdf():
    print("Testing PDF Download...")
    data = {
        "filename": "test.docx",
        "summary": "This is a test.",
        "errors": {
            "summary": {"total": 1},
            "spelling": [{"word": "teh", "suggestion": "the"}]
        }
    }
    res = requests.post("http://localhost:5000/api/download-report", json=data)
    print("PDF Status:", res.status_code)
    if res.status_code != 200:
        print("PDF Error:", res.text)

def test_docx():
    print("Testing DOCX Download...")
    # Create a dummy docx
    import docx
    import io
    doc = docx.Document()
    doc.add_paragraph("This is teh test.")
    buffer = io.BytesIO()
    doc.save(buffer)
    
    files = {"file": ("test.docx", buffer.getvalue(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    res = requests.post("http://localhost:5000/api/download-corrected", files=files)
    print("DOCX Status:", res.status_code)
    if res.status_code != 200:
        print("DOCX Error:", res.text)

if __name__ == "__main__":
    test_pdf()
    test_docx()
