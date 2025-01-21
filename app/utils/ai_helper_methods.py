from .config import config
import os
import gc
import numpy as np
import faiss
import redis
from app.models.user import User
from typing import List, Dict
from app.models.document import Document
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

def fetch_document_content(document_ids: List[int], user_id) -> Dict[int, str]:
    """
    Fetches the content of documents by their IDs.
    """
    try:
        if not document_ids:
            logger.warning("Empty document IDs provided.")
            return {"error": "No documents found"}
        
        documents = Document.query.with_entities(Document.content).filter(
            Document.id.in_(document_ids),
            (Document.user_id == user_id) | (Document.source == 'okms')
        ).all()

        if not documents:
            logger.warning("No documents found for the given IDs.")
            return {"error": "No documents found"}

        document_contents = "\n\n".join([doc.content for doc in documents])
        return document_contents

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

 
def search_documents(query):
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
        
        search_result = {'ids': ids}
        set_in_cache(query_hash, search_result)
        logger.info("Search result cached.")
        
        return search_result
    except Exception as e:
        logger.error(f"Error during FAISS search: {e}", exc_info=True)
        raise RuntimeError("An error occurred during document search") from e


def get_prompt(document_context, user_query, user_role):
    prompt = (
        f"In this chat, your name is Brain:\n\n"
        f"TCG stands for The Concept Group, a company located in Nigeria. "
        f"The Concept Group specializes in financial services, technology, and business solutions. "
        f"You should always assume 'TCG' refers to The Concept Group.\n\n"
        f"You are an AI assistant for answering all TCG-related questions and general questions too:\n\n"
        f"Use the following TCG documents to answer the user's question if applicable:\n\n"
        f"{document_context}\n\n"
        f"You should also answer questions as a professional {user_role}.\n\n"
        f"Question: {user_query}"
    )
    return prompt

def fetch_user_role(user_id):
    try:
        if not user_id or not isinstance(user_id, int):
            raise ValueError("Invalid user_id provided.")
        
        user = User.query.get(user_id)
        
        if not user:
            logger.warning(f"User with ID {user_id} not found.")
            return {"error": "User not found"}
        
        return user.job_role
    
    except Exception as e:
        logger.error(f"Error fetching user role for ID {user_id}: {e}")
        return {"error": str(e)}
    


