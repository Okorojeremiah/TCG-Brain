from .config import config
import os
import gc
import numpy as np
import faiss
from typing import List, Dict
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
from app.models.database import db
from app.utils.logger import logger
from sentence_transformers import SentenceTransformer
import hashlib
import threading 
from app.exceptions.faissInitializationError import FaissInitializationError
from app.utils.redis import get_from_cache, set_in_cache




index_lock = threading.Lock()
index = None 



def get_model():
    return SentenceTransformer(config.HUGGING_FACE_TRANSFORMER)

from typing import List, Dict
from sqlalchemy.orm import joinedload
from sqlalchemy import or_

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
from app.models.database import db
from app.utils.logger import logger

def fetch_document_content(document_ids: List[int], user_id: int, user_department: str) -> Dict[int, str]:
    """
    Fetches the content of documents by their IDs, considering user-specific, department-specific, and general documents.
    """
    try:
        if not document_ids:
            logger.warning("Empty document IDs provided.")
            return {"error": "No documents found"}

        # Fetch user-specific documents
        user_documents = Document.query.with_entities(Document.content).filter(
            Document.id.in_(document_ids),
            Document.user_id == user_id
        ).all()

        # Fetch department-specific documents based on the user's department
        department_documents = []
        if user_department == 'hr':
            department_documents = HRDocument.query.with_entities(HRDocument.content).filter(
                HRDocument.id.in_(document_ids)
            ).all()
        elif user_department == 'it':
            department_documents = ITDocument.query.with_entities(ITDocument.content).filter(
                ITDocument.id.in_(document_ids)
            ).all()
        elif user_department == 'reconciliation':
            department_documents = ReconciliationDocument.query.with_entities(ReconciliationDocument.content).filter(
                ReconciliationDocument.id.in_(document_ids)
            ).all()
        elif user_department == 'marketing':
            department_documents = MarketingDocument.query.with_entities(MarketingDocument.content).filter(
                MarketingDocument.id.in_(document_ids)
            ).all()
        elif user_department == 'transformation':
            department_documents = TransformationDocument.query.with_entities(TransformationDocument.content).filter(
                TransformationDocument.id.in_(document_ids)
            ).all()
        elif user_department == 'communication':
            department_documents = CommunicationDocument.query.with_entities(CommunicationDocument.content).filter(
                CommunicationDocument.id.in_(document_ids)
            ).all()
        elif user_department == 'internal_operations':
            department_documents = InternalOperationDocument.query.with_entities(InternalOperationDocument.content).filter(
                InternalOperationDocument.id.in_(document_ids)
            ).all()
        elif user_department == 'legal':
            department_documents = LegalDocument.query.with_entities(LegalDocument.content).filter(
                LegalDocument.id.in_(document_ids)
            ).all()
        elif user_department == 'accounts':
            department_documents = AccountDocument.query.with_entities(AccountDocument.content).filter(
                AccountDocument.id.in_(document_ids)
            ).all()
        elif user_department == 'portfolio_risk':
            department_documents = PortfolioRiskDocument.query.with_entities(PortfolioRiskDocument.content).filter(
                PortfolioRiskDocument.id.in_(document_ids)
            ).all()
        elif user_department == 'underwriting':
            department_documents = UnderwriterDocument.query.with_entities(UnderwriterDocument.content).filter(
                UnderwriterDocument.id.in_(document_ids)
            ).all()
        elif user_department == 'business_operations':
            department_documents = BusinessOperationDocument.query.with_entities(BusinessOperationDocument.content).filter(
                BusinessOperationDocument.id.in_(document_ids)
            ).all()
        elif user_department == 'client_experience':
            department_documents = ClientExperienceDocument.query.with_entities(ClientExperienceDocument.content).filter(
                ClientExperienceDocument.id.in_(document_ids)
            ).all()
        elif user_department == 'recovery':
            department_documents = RecoveryDocument.query.with_entities(RecoveryDocument.content).filter(
                RecoveryDocument.id.in_(document_ids)
            ).all()
        elif user_department == 'product':
            department_documents = ProductDocument.query.with_entities(ProductDocument.content).filter(
                ProductDocument.id.in_(document_ids)
            ).all()
        elif user_department == 'sales':
            department_documents = SalesDocument.query.with_entities(SalesDocument.content).filter(
                SalesDocument.id.in_(document_ids)
            ).all()
        else:
            logger.warning(f"Unknown department: {user_department}")

        # Fetch general documents
        general_documents = GeneralDocument.query.with_entities(GeneralDocument.content).filter(
            GeneralDocument.id.in_(document_ids)
        ).all()

        # Combine all documents
        all_documents = user_documents + department_documents + general_documents

        if not all_documents:
            logger.warning("No documents found for the given IDs.")
            return {"error": "No documents found"}

        # Combine document content
        document_contents = "\n\n".join([doc.content for doc in all_documents])

        return {"content": document_contents}
    except Exception as e:
        logger.error(f"Error fetching document content: {e}")
        return {"error": str(e)}
    
def clear_faiss_index():
    index.reset()
    logger.info("index cleared successfully")
    
def load_faiss_index():
    global index
    try:
        with index_lock:
            if config.FAISS_INDEX_FILE and os.path.exists(config.FAISS_INDEX_FILE):
                index = faiss.read_index(config.FAISS_INDEX_FILE)
            
                logger.info(f"FAISS index loaded from {config.FAISS_INDEX_FILE}")
            else:
                index = create_new_index()
                logger.info("New FAISS index created since no file was found.")
    except Exception as e:
        logger.error(f"Failed to initialize FAISS index: {e}")
        raise FaissInitializationError("FAISS index initialization failed") from e
    

def create_new_index():
    global index
    index = faiss.IndexHNSWFlat(384, 32) 
    return faiss.IndexIDMap(index)

def generate_embedding(document):
    try:
        doc_hash = hash_query(document)
     
        cached_embedding = get_from_cache(doc_hash)
        if cached_embedding:
            logger.info("Embedding retrieved from cache.")
            return cached_embedding
        
        model = get_model()
        embedding = model.encode(document).tolist()
        if not isinstance(embedding, list) or len(embedding) != 384:
            raise ValueError("Invalid embedding format.")
        
        
        set_in_cache(doc_hash, embedding)
        logger.info("Embedding computed and cached.")
        return embedding
    except Exception as e:
        logger.error(f"Error generating embedding: {e}", exc_info=True)
        raise

def add_doc_with_id_to_faiss(document, doc_id):
    """
    Adds a document to the FAISS index
    """
    try:
        embedding = generate_embedding(document)
        
        global index
        if index is None:
            raise RuntimeError("FAISS index not initialized")
        
        
        # Create numpy arrays for the document embedding and doc ids
        embeddings = np.array([embedding]).astype('float32')
        ids = np.array([doc_id], dtype='int64')
        
        index.add_with_ids(embeddings, ids)

        # Save the FAISS index to a file
        faiss.write_index(index, config.FAISS_INDEX_FILE)
    except Exception as e:
        logger.error(f"Error adding document to FAISS index: {e}", exc_info=True)
        raise
    finally:
        del embedding
        gc.collect()


    
def index_contains_document(doc_id):
    global index
    if index is None:
        return False
    with index_lock:
        return np.any(index.id_map == doc_id)


def hash_query(query: str) -> str:
    """
    Hashes a query string for use as a cache key.
    """
    return hashlib.sha256(query.encode()).hexdigest()


def search_documents(query, user_id, user_department):
    """
    Searches the FAISS index for documents matching the query.
    """
    
    try:
        global index
        if index is None:
            raise RuntimeError("FAISS index not initialized")
        
        query_hash = hash_query(query)

        # Check Redis cache for search results
        cached_result = get_from_cache(query_hash)
        if cached_result:
            logger.info("Search result retrieved from cache.")
            return cached_result
        
        # Generate query embedding
        embedding = np.array([generate_embedding(query)]).astype('float32')
        
        # Search the index
        distances, I = index.search(embedding, 10)
        
        ids = I.tolist()[0]
        logger.info(f"Search returned IDs: {ids}")
        
        # Fetch user-specific or general documents
        user_documents = fetch_document_content(ids, user_id, user_department)
        
        search_result = {'content': user_documents}
        set_in_cache(query_hash, search_result)
        logger.info("Search result cached.")
        
        return search_result
    except Exception as e:
        logger.error(f"Error during FAISS search: {e}", exc_info=True)
        raise RuntimeError("An error occurred during document search") from e


def get_prompt(document_context, user_query, user_role, chat_history):
    """
    Creates a prompt for the AI that incorporates chat history for better contextual understanding.
    """
    history_context = "\n".join([f"{msg['sender']}: {msg['content']}" for msg in chat_history])

    prompt = (
        f"Your name is Brain. TCG refers to The Concept Group (Nigeria), specializing in financial services, technology, and business solutions.  Answer the following prompt using your knowledge and the provided context, drawing upon the documents where applicable.\n\n"
        f"Chat History:\n{history_context}\n\n"
        f"Documents:\n{document_context}\n\n"
        f"User Role: {user_role} (Answer in a style appropriate for this professional role.)\n\n"
        f'Keep your responses conversational, context-aware, and polite. Also, avoid repetitive statements like: "based on the provided document", "as brain".\n\n'
        f"Question: {user_query}\n\n"
    )
    return prompt


    


