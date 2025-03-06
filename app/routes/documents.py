from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.verify_session import verify_session
from app.utils.upload_validation import validate_file
from app.services.file_processing import (
    save_file, 
    save_general_files, 
    compress_doc,
    save_account_files,
    save_businessOps_files,
    save_client_experience_files,
    save_communication_files,
    save_hr_files,
    save_internalOps_files,
    save_it_files,
    save_legal_files,
    save_marketing_files,
    save_portfolio_files,
    save_product_files,
    save_reconciliation_files,
    save_recovery_files, 
    save_sales_files, 
    save_transformation_files, 
    save_underwriter_files
)
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
    print(identity)
    session_response = verify_session(identity)
    user_id = session_response.get("user_id")
    is_superuser = session_response.get("is_superuser")
    user_department = session_response.get("department")  
    
    # Ensure only superusers can upload documents
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

        # Determine which table to save the document based on the user's department
        if user_department == "admin":
            # Save to GeneralDocument table
            document = save_general_files(user_id, compressed_file, file_type, text)
        else:
            # Save to the respective department table
            if user_department == "hr":
                document = save_hr_files(user_id, compressed_file, file_type, text)
            elif user_department == "it":
                document = save_it_files(user_id, compressed_file, file_type, text)
            elif user_department == "reconciliation":
                document = save_reconciliation_files(user_id, compressed_file, file_type, text)
            elif user_department == "marketing":
                document = save_marketing_files(user_id, compressed_file, file_type, text)
            elif user_department == "transformation":
                document = save_transformation_files(user_id, compressed_file, file_type, text)
            elif user_department == "communication":
                document = save_communication_files(user_id, compressed_file, file_type, text)
            elif user_department == "internal_operation":
                document = save_internalOps_files(user_id, compressed_file, file_type, text)
            elif user_department == "legal":
                document = save_legal_files(user_id, compressed_file, file_type, text)
            elif user_department == "account":
                document = save_account_files(user_id, compressed_file, file_type, text)
            elif user_department == "portfolio_risk":
                document = save_portfolio_files(user_id, compressed_file, file_type, text)
            elif user_department == "underwriter":
                document = save_underwriter_files(user_id, compressed_file, file_type, text)
            elif user_department == "business_operation":
                document = save_businessOps_files(user_id, compressed_file, file_type, text)
            elif user_department == "client_experience":
                document = save_client_experience_files(user_id, compressed_file, file_type, text)
            elif user_department == "recovery":
                document = save_recovery_files(user_id, compressed_file, file_type, text)
            elif user_department == "product":
                document = save_product_files(user_id, compressed_file, file_type, text)
            elif user_department == "sales":
                document = save_sales_files(user_id, compressed_file, file_type, text)
            else:
                return jsonify({"error": "Invalid department"}), 400

        # Add the document to FAISS for indexing
        add_doc_with_id_to_faiss(document.content, document.id)

        return jsonify({
            "message": f"Document uploaded successfully to {user_department} department",
            "file_name": document.file_name,
            "file_type": document.file_type,
            "extracted_text": text[:500]  # Return the first 500 characters of the extracted text
        }), 200
    except Exception as e:
        logger.error(f"Error uploading document: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500   
    