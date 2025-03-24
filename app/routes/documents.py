from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.verify_session import verify_session
from app.utils.upload_validation import validate_file
from app.services.file_processing import generate_docx_from_text, generate_pdf_from_text, generate_pptx_from_text, generate_xls_from_text, generate_xlsx_from_text
from flask import send_file
from io import BytesIO
from app.models.user import User
from app.models.document import (
    Document, 
    GeneralDocument,
    HRDocument,
    ITDocument,
    ReconciliationDocument,
    MarketingDocument,
    TransformationDocument,
    CommunicationDocument,
    InternalOperationDocument,
    LegalDocument,
    AccountDocument,
    PortfolioRiskDocument,
    UnderwriterDocument,
    BusinessOperationDocument,
    ClientExperienceDocument,
    RecoveryDocument,
    ProductDocument,
    SalesDocument,
)
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



@documents_bp.route('/upload', methods=['OPTIONS', 'POST'])
@jwt_required()
def upload_document():
    if request.method == 'OPTIONS':
        return '', 204

    identity = get_jwt_identity()
    session_response = verify_session(identity)
    user_id = session_response.get("user_id")
    user_department = session_response.get("department")  

    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    visibility = request.form.get("visibility", "department")  
    
    try:
        logger.info("Starting file compression.")
        compressed_file = compress_doc(file)
        logger.info("File compression completed.")

        response = validate_file(compressed_file)
        if "error" in response:
            return jsonify(response), 400

        text = response.get("text")
        file_type = response.get("file_extension")

        # Determine where to save based on visibility
        if visibility == "general":
            document = save_general_files(user_id, compressed_file, file_type, text)
        elif visibility == "personal":
            document = save_file(user_id, compressed_file, file_type, text)
        else:  # department visibility
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
            elif user_department == "internal_operations":
                document = save_internalOps_files(user_id, compressed_file, file_type, text)
            elif user_department == "legal":
                document = save_legal_files(user_id, compressed_file, file_type, text)
            elif user_department == "accounts":
                document = save_account_files(user_id, compressed_file, file_type, text)
            elif user_department == "portfolio_risk":
                document = save_portfolio_files(user_id, compressed_file, file_type, text)
            elif user_department == "underwriting":
                document = save_underwriter_files(user_id, compressed_file, file_type, text)
            elif user_department == "business_operations":
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

        add_doc_with_id_to_faiss(document.content, document.id)

        return jsonify({
            "message": f"Document uploaded successfully with {visibility} visibility",
            "file_name": document.file_name,
            "file_type": document.file_type,
            "extracted_text": text[:500]
        }), 200
    except Exception as e:
        logger.error(f"Error uploading document: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500



@documents_bp.route('/accessible-documents', methods=['OPTIONS', 'GET'])
@jwt_required()
def get_accessible_documents():
    if request.method == 'OPTIONS':
        return '', 204

    identity = get_jwt_identity()
    session_response = verify_session(identity)
    user_id = session_response.get("user_id")
    user_department = session_response.get("department")

    if "error" in session_response:
        return jsonify(session_response), 401

    try:
        # Fetch general documents with uploader's name
        general_documents = GeneralDocument.query.join(
            User, GeneralDocument.uploaded_by == User.id
        ).with_entities(
            GeneralDocument.id,
            GeneralDocument.file_name,
            GeneralDocument.file_type,
            GeneralDocument.upload_date,
            User.name.label("uploader")  # Include uploader's name
        ).all()

        # Fetch department-specific documents with uploader's name
        department_documents = []
        if user_department == 'hr':
            department_documents = HRDocument.query.join(
                User, HRDocument.uploaded_by == User.id
            ).with_entities(
                HRDocument.id,
                HRDocument.file_name,
                HRDocument.file_type,
                HRDocument.upload_date,
                User.name.label("uploader")  # Include uploader's name
            ).all()
        elif user_department == 'it':
            department_documents = ITDocument.query.join(
                User, ITDocument.uploaded_by == User.id
            ).with_entities(
                ITDocument.id,
                ITDocument.file_name,
                ITDocument.file_type,
                ITDocument.upload_date,
                User.name.label("uploader")  # Include uploader's name
            ).all()
        elif user_department == "reconciliation":
            department_documents = ReconciliationDocument.query.join(
                User, ReconciliationDocument.uploaded_by == User.id
            ).with_entities(
                ReconciliationDocument.id,
                ReconciliationDocument.file_name,
                ReconciliationDocument.file_type,
                ReconciliationDocument.upload_date,
                User.name.label("uploader")  # Include uploader's name
            ).all()
        elif user_department == 'marketing':
            department_documents = MarketingDocument.query.join(
                User, MarketingDocument.uploaded_by == User.id
            ).with_entities(
                MarketingDocument.id,
                MarketingDocument.file_name,
                MarketingDocument.file_type,
                MarketingDocument.upload_date,
                User.name.label("uploader")  # Include uploader's name
            ).all()
        elif user_department == 'transformation':
            department_documents = TransformationDocument.query.join(
                User, TransformationDocument.uploaded_by == User.id
            ).with_entities(
                TransformationDocument.id,
                TransformationDocument.file_name,
                TransformationDocument.file_type,
                TransformationDocument.upload_date,
                User.name.label("uploader")  # Include uploader's name
            ).all()
        elif user_department == 'communication':
            department_documents = CommunicationDocument.query.join(
                User, CommunicationDocument.uploaded_by == User.id
            ).with_entities(
                CommunicationDocument.id,
                CommunicationDocument.file_name,
                CommunicationDocument.file_type,
                CommunicationDocument.upload_date,
                User.name.label("uploader")  # Include uploader's name
            ).all()
        elif user_department == 'internal_operations':
            department_documents = InternalOperationDocument.query.join(
                User, InternalOperationDocument.uploaded_by == User.id
            ).with_entities(
                InternalOperationDocument.id,
                InternalOperationDocument.file_name,
                InternalOperationDocument.file_type,
                InternalOperationDocument.upload_date,
                User.name.label("uploader")  # Include uploader's name
            ).all()
        elif user_department == 'legal':
            department_documents = LegalDocument.query.join(
                User, LegalDocument.uploaded_by == User.id
            ).with_entities(
                LegalDocument.id,
                LegalDocument.file_name,
                LegalDocument.file_type,
                LegalDocument.upload_date,
                User.name.label("uploader")  # Include uploader's name
            ).all()
        elif user_department == 'accounts':
            department_documents = AccountDocument.query.join(
                User, AccountDocument.uploaded_by == User.id
            ).with_entities(
                AccountDocument.id,
                AccountDocument.file_name,
                AccountDocument.file_type,
                AccountDocument.upload_date,
                User.name.label("uploader")  # Include uploader's name
            ).all()
        elif user_department == 'portfolio_risk':
            department_documents = PortfolioRiskDocument.query.join(
                User, PortfolioRiskDocument.uploaded_by == User.id
            ).with_entities(
                PortfolioRiskDocument.id,
                PortfolioRiskDocument.file_name,
                PortfolioRiskDocument.file_type,
                PortfolioRiskDocument.upload_date,
                User.name.label("uploader")  # Include uploader's name
            ).all()
        elif user_department == 'underwriting':
            department_documents = UnderwriterDocument.query.join(
                User, UnderwriterDocument.uploaded_by == User.id
            ).with_entities(
                UnderwriterDocument.id,
                UnderwriterDocument.file_name,
                UnderwriterDocument.file_type,
                UnderwriterDocument.upload_date,
                User.name.label("uploader")  # Include uploader's name
            ).all()
        elif user_department == 'business_operations':
            department_documents = BusinessOperationDocument.query.join(
                User, BusinessOperationDocument.uploaded_by == User.id
            ).with_entities(
                BusinessOperationDocument.id,
                BusinessOperationDocument.file_name,
                BusinessOperationDocument.file_type,
                BusinessOperationDocument.upload_date,
                User.name.label("uploader")  # Include uploader's name
            ).all()
        elif user_department == 'client_experience':
            department_documents = ClientExperienceDocument.query.join(
                User, ClientExperienceDocument.uploaded_by == User.id
            ).with_entities(
                ClientExperienceDocument.id,
                ClientExperienceDocument.file_name,
                ClientExperienceDocument.file_type,
                ClientExperienceDocument.upload_date,
                User.name.label("uploader")  # Include uploader's name
            ).all()
        elif user_department == 'recovery':
            department_documents = RecoveryDocument.query.join(
                User, RecoveryDocument.uploaded_by == User.id
            ).with_entities(
                RecoveryDocument.id,
                RecoveryDocument.file_name,
                RecoveryDocument.file_type,
                RecoveryDocument.upload_date,
                User.name.label("uploader")  # Include uploader's name
            ).all()
        elif user_department == 'product':
            department_documents = ProductDocument.query.join(
                User, ProductDocument.uploaded_by == User.id
            ).with_entities(
                ProductDocument.id,
                ProductDocument.file_name,
                ProductDocument.file_type,
                ProductDocument.upload_date,
                User.name.label("uploader")  # Include uploader's name
            ).all()
        elif user_department == 'sales':
            department_documents = SalesDocument.query.join(
                User, SalesDocument.uploaded_by == User.id
            ).with_entities(
                SalesDocument.id,
                SalesDocument.file_name,
                SalesDocument.file_type,
                SalesDocument.upload_date,
                User.name.label("uploader")  # Include uploader's name
            ).all()

        # Fetch user-specific documents with uploader's name
        user_documents = Document.query.join(
        User, Document.user_id == User.id
            ).with_entities(
                Document.id,
                Document.file_name,
                Document.file_type,
                Document.upload_date,
                User.name.label("uploader")
            ).filter(Document.user_id == user_id).all()


        # Combine all documents
        accessible_documents = general_documents + department_documents + user_documents

        # Convert to a list of dictionaries
        documents_list = [{
            "id": doc.id,
            "file_name": doc.file_name,
            "file_type": doc.file_type,
            "upload_date": doc.upload_date.strftime('%Y-%m-%d %H:%M:%S'),
            "uploader": doc.uploader  # Include uploader's name
        } for doc in accessible_documents]

        return jsonify({"documents": documents_list}), 200

    except Exception as e:
        logger.error(f"Error fetching accessible documents: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    

@documents_bp.route('/download/<int:document_id>', methods=['OPTIONS', 'GET'])
@jwt_required()
def download_document(document_id):
    if request.method == 'OPTIONS':
        return '', 204

    identity = get_jwt_identity()
    session_response = verify_session(identity)
    user_id = session_response.get("user_id")
    user_department = session_response.get("department")

    if "error" in session_response:
        return jsonify(session_response), 401

    try:
        # Define mimetypes mapping for file types
        mimetypes = {
            'pdf': 'application/pdf',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'xls': 'application/vnd.ms-excel'
        }
        
        # Try to fetch a general document first
        document = GeneralDocument.query.filter_by(id=document_id).first()
        if document:
            file_ext = document.file_type.lower() if document.file_type else 'txt'
            mimetype = mimetypes.get(file_ext, 'text/plain')
            content_bytes = generate_file_content(document)
            return send_file(
                content_bytes,
                download_name=document.file_name,
                mimetype=mimetype,
                as_attachment=True
            )

        # Check department-specific documents
        if user_department == 'hr':
            document = HRDocument.query.filter_by(id=document_id).first()
        elif user_department == 'it':
            document = ITDocument.query.filter_by(id=document_id).first()
        elif user_department == 'reconciliation':
            document = ReconciliationDocument.query.filter_by(id=document_id).first()
        elif user_department == 'marketing':
            document = MarketingDocument.query.filter_by(id=document_id).first()
        elif user_department == 'transformation':
            document = TransformationDocument.query.filter_by(id=document_id).first()
        elif user_department == 'communication':
            document = CommunicationDocument.query.filter_by(id=document_id).first()
        elif user_department == 'internal_operations':
            document = InternalOperationDocument.query.filter_by(id=document_id).first()
        elif user_department == 'legal':
            document = LegalDocument.query.filter_by(id=document_id).first()
        elif user_department == 'accounts':
            document = AccountDocument.query.filter_by(id=document_id).first()
        elif user_department == 'portfolio_risk':
            document = PortfolioRiskDocument.query.filter_by(id=document_id).first()
        elif user_department == 'underwriting':
            document = UnderwriterDocument.query.filter_by(id=document_id).first()
        elif user_department == 'business_operations':
            document = BusinessOperationDocument.query.filter_by(id=document_id).first()
        elif user_department == 'client_experience':
            document = ClientExperienceDocument.query.filter_by(id=document_id).first()
        elif user_department == 'recovery':
            document = RecoveryDocument.query.filter_by(id=document_id).first()
        elif user_department == 'product':
            document = ProductDocument.query.filter_by(id=document_id).first()
        elif user_department == 'sales':
            document = SalesDocument.query.filter_by(id=document_id).first()
        else:
            document = None

        if document:
            file_ext = document.file_type.lower() if document.file_type else 'txt'
            mimetype = mimetypes.get(file_ext, 'text/plain')
            content_bytes = generate_file_content(document)
            return send_file(
                content_bytes,
                download_name=document.file_name,
                mimetype=mimetype,
                as_attachment=True
            )
        
        #check if the document is user-specific
        document = Document.query.filter_by(id=document_id, user_id=user_id).first()
       
        if document:
            file_ext = document.file_type.lower() if document.file_type else 'txt'
            mimetype = mimetypes.get(file_ext)
            logger.info(mimetype)
            content_bytes = generate_file_content(document)
            return send_file(
                content_bytes,
                download_name=document.file_name,
                mimetype=mimetype,
                as_attachment=True
            )
        
        return jsonify({"error": "Document not found or access denied"}), 404

    except Exception as e:
        logger.error(f"Error downloading document: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    

def generate_file_content(document):
            file_ext = document.file_type.lower() if document.file_type else 'txt'
            if file_ext == 'docx':
                return generate_docx_from_text(document.content)
            elif file_ext == 'pptx':
                return generate_pptx_from_text(document.content)
            elif file_ext == 'xlsx':
                return generate_xlsx_from_text(document.content)
            elif file_ext == 'xls':
                return generate_xls_from_text(document.content)
            elif file_ext == 'pdf':
                return generate_pdf_from_text(document.content)
            else:
                # Default: return plain text as bytes
                output = BytesIO(document.content.encode('utf-8'))
                output.seek(0)
                return output

