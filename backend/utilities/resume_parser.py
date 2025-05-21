import docx2txt
import PyPDF2
import os

def parse_resume(resume_file):
    ext = os.path.splitext(resume_file.filename)[1]
    if ext == ".pdf":
        reader = PyPDF2.PdfReader(resume_file)
        text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
    elif ext == ".docx":
        text = docx2txt.process(resume_file)
    else:
        text = resume_file.read().decode("utf-8")
    return text
