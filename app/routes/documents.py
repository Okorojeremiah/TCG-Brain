from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.verify_session import verify_session
from app.utils.upload_validation import validate_file
from app.services.file_processing import save_file, save_general_files, compress_doc
from app.utils.ai_helper_methods import add_doc_with_id_to_faiss
from app.utils.logger import logger


documents_bp = Blueprint('documents', __name__, url_prefix='/documents')



@documents_bp.route("/upload", methods=["OPTIONS", "POST"])
@jwt_required()
def upload_document():
    if request.method == 'OPTIONS':
        return '', 204
    identity = get_jwt_identity()
    session_response = verify_session(identity)
    user_id = session_response.get("user_id")
    
    if "error" in session_response:
        return jsonify(session_response), 401

    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    try:
        logger.info("Starting file compression.")
        compressed_file = compress_doc(file)
        logger.info("File compression completed.")

        # Validate and process the file
        logger.debug("Validating file.")
        response = validate_file(compressed_file)
        if "error" in response:
            logger.error(f"File validation failed: {response['error']}")
            return jsonify(response), 400

        text = response.get("text")
        file_type = response.get("file_extension")

        # Save file metadata and content to the database
        logger.debug("Saving file to database.")
        document = save_file(user_id, compressed_file, file_type, text)
        add_doc_with_id_to_faiss(document.content, document.id)
        
        logger.debug("File uploaded and processed successfully.")
        return jsonify({
            "message": "File uploaded and processed successfully",
            "file_name": document.file_name,
            "file_type": document.file_type,
            "extracted_text": text[:500]
        }), 200
    except ValueError as e:
        logger.error(f"ValueError: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500
    


@documents_bp.route('/admin/upload', methods=['OPTIONS', 'POST'])
@jwt_required()
def admin_upload_document():
    if request.method == 'OPTIONS':
        return '', 204
    
    identity = get_jwt_identity()
    session_response = verify_session(identity)
    user_id = session_response.get("user_id")
    is_superuser = session_response.get("is_superuser")

    if not is_superuser:
        return jsonify({"error": "Unauthorized access"}), 403

    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    try:
        logger.info("Starting file compression.")
        compressed_file = compress_doc(file)
        logger.info("File compression completed.")
        
        response = validate_file(compressed_file)
        if "error" in response:
            return jsonify(response), 400

        text = response.get("text")
        file_type = response.get("file_extension")

        # Save general document
        document = save_general_files(user_id, compressed_file, file_type, text)
        add_doc_with_id_to_faiss(document.content, document.id)
        
        return jsonify({
            "message": "General document uploaded successfully",
            "file_name": document.file_name,
            "file_type": document.file_type,
            "extracted_text": text[:500]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500    
    