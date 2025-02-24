from docx import Document as DocxDocument
from pptx import Presentation
from datetime import datetime
import PyPDF2
import openpyxl
from app.models.document import Document
from app.models.database import db


def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text


def extract_text_from_word(docx_path):
    doc = DocxDocument(docx_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + '\n'
    return text


def extract_text_from_ppt(pptx_path):
    presentation = Presentation(pptx_path)
    text = ""
    for slide in presentation.slides:
        for shape in slide.shapes:
            if hasattr(shape, 'text'):
                text += shape.text + '\n'
    return text

def extract_text_from_excel(excel_path):
    wb = openpyxl.load_workbook(excel_path, data_only=True)
    text = ""
    for sheet in wb.worksheets:
        for row in sheet.iter_rows(values_only=True):
            row_text = " ".join([str(cell) for cell in row if cell is not None])
            text += row_text + "\n"
    return text

def save_file(user_id, file, file_extension, text):
        
        document = Document(
            user_id=user_id,
            file_name=file.filename,
            file_type=file_extension,
            upload_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            content=text
        )
        
        db.session.add(document)
        db.session.commit()
        return document  
