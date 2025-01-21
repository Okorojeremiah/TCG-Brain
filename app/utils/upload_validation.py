import os
from werkzeug.utils import secure_filename
from app.services.file_processing import extract_text_from_pdf, extract_text_from_ppt, extract_text_from_word
from .config import config
from app.models.document import Document

def allowed_file(filename, allowed_extensions):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions

def validate_file(file):
    if file.filename == '':
        return {"error": "No selected file", "status": 400}
    
    # Ensure the file does not already exist in the database
    if Document.query.filter_by(file_name=file.filename).first():   
        return {"error": "File already exists", "status": 400}
    
    # Check file extension and process accordingly
    if file and allowed_file(file.filename, {"pdf", "docx", "txt", "pptx"}):
        filename = secure_filename(file.filename)
        os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
        filepath = os.path.join(config.UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Determine file extension
        file_extension = os.path.splitext(filename)[1][1:].lower()
        text = ""

        try:
            # Extract text based on file type
            if file_extension == 'pdf':
                text = extract_text_from_pdf(filepath)
            elif file_extension == 'docx':
                text = extract_text_from_word(filepath)
            elif file_extension == 'pptx':
                text = extract_text_from_ppt(filepath)
            else:
                return {"error": f"Unsupported file type: {file_extension}", "status": 400}
            
            text = text.encode('utf-8', 'ignore').decode('utf-8')

            return {"file_extension": file_extension, "text": text}
        except Exception as e:
            # Log or handle specific extraction errors
            return {"error": f"Failed to process file: {str(e)}", "status": 500}
    else:
        return {"error": "File type not allowed", "status": 400}
