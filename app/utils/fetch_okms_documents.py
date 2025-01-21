
from app.utils.config import config
from flask import current_app
from app.models.database import db
from app.utils.logger import logger
from werkzeug.utils import secure_filename
from app.utils.upload_validation import allowed_file
from app.services.file_processing import extract_text_from_pdf, extract_text_from_ppt, extract_text_from_word
from app.models.document import Document
from app.utils.logger import logger
from app.models.database import db
from app.utils.ai_helper_methods import add_doc_with_id_to_faiss, index_contains_document
from sqlalchemy.exc import SQLAlchemyError


    
# def fetch_okms_documents(app):
#     with app.app_context():
#         engine = db.get_engine(bind_key='okms')
#         with engine.connect() as connection:
#             results = connection.exec_driver_sql("SELECT * FROM documents")
            
#             # Format results
#             documents = [{"id": d.id} for d in results]
#             return {"documents": documents}
        
def fetch_okms_document_contents(engine):
    """
    Fetches and extracts text content from documents stored in the 'okms' database.

    Returns:
        dict: A dictionary containing the extracted text or error messages.
    """
    try:
             # Get the engine for the 'okms' bind
            with engine.connect() as connection:
                # Fetch document data from the database
                results = connection.exec_driver_sql(
                    "SELECT id, file_name, content, file_type FROM documents"
                )

                documents = []
                for row in results:
                    try:
                        # Extract file attributes
                        document_id = row.id
                        file_name = row.file_name
                        file_content = row.content  # Binary content or plain text
                        file_extension = row.file_type

                        # Append document data to the result list
                        documents.append({
                            "id": document_id,
                            "file_name": file_name,
                            "file_extension": file_extension,
                            "text": file_content,
                        })
                        
                    except Exception as e:
                        # Handle errors for individual documents
                        logger.error(f"Error processing document ID {document_id}: {e}")
                        documents.append({
                            "id": document_id,
                            "error": f"Failed to process file: {str(e)}"
                        })

                return {"status": 200, "documents": documents}

    except Exception as e:
        logger.error(f"Error fetching or processing documents: {e}")
        return {"status": 500, "error": f"Failed to fetch documents: {str(e)}"}


def get_okms_contents_with_engine():
    """Fetch OKMS document contents within the app context."""
    # if not current_app:
    #     raise RuntimeError("Function must be called within an app context.")
    
    
    engine = db.get_engine(bind_key='okms')
    return fetch_okms_document_contents(engine)


def save_okms_documents(app):  
    with app.app_context():
        try:
            okms_response = get_okms_contents_with_engine()
            
            if okms_response["status"] == 200:
                documents = okms_response["documents"]
                
                for doc in documents:
                    try:
                        document_id = doc.get("id")
                        file_extension = doc.get("file_extension")
                        content = doc.get("text", "")
                        name = doc.get("file_name")
                        
                        if not document_id or not content:
                            logger.warning(f"Skipping invalid document: {doc}")
                            continue
                        
                        existing_document = Document.query.filter_by(id=document_id, source='okms').first()
                        
                        if existing_document:
                            logger.info(f"Document with ID {document_id} already exists. Skipping.")
                            continue
                        
                        new_doc = Document(
                            id=document_id,
                            file_name=name,
                            file_type=file_extension,
                            content=content,
                            source='okms',
                        )
                        db.session.add(new_doc)
                        db.session.commit()
                        
                        logger.info("Inserted new document", extra={"document_id": document_id, "source": "okms"})
                        
                        if not index_contains_document(document_id):
                            add_doc_with_id_to_faiss(new_doc.content, new_doc.id)
                            logger.info(f"Document {document_id} added to FAISS index.")
                            
                    except SQLAlchemyError as db_error:
                        db.session.rollback()
                        logger.error(f"Database error for document {doc.get('id')}: {db_error}") 
                            
                    except Exception as doc_error:
                        logger.error(f"Failed to process document {doc.get('id')}: {doc_error}")
                logger.info("Document synchronization completed.")
            else:
                logger.error(f"Failed to fetch documents from OKMS: {okms_response.get('error')}")
        except Exception as e:
            logger.error(f"Error in fetch_and_save_documents: {e}", exc_info=True)
        finally:
            db.session.close()
            
