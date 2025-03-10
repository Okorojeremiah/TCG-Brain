from app.models.database import db
from app.models.chat import Chat
from datetime import datetime
from app.utils.logger import logger
import re
import json
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from sqlalchemy.exc import IntegrityError, OperationalError



def create_chat_instance(user_id, session_id):
    try:
        chat = Chat (
            user_id=user_id,
            session_id=session_id,
            name=None,
            started_at=datetime.now()
        )
        db.session.add(chat)
        db.session.commit()
        return chat
    except Exception as e:
        logger.error(f"Error saving chat: {e}", exc_info=True)
        raise
    
def get_or_create_default_chat(user_id, session_id):
    """
    Ensures the user has a default chat session.
    If none exists, create one.
    """
    chat = Chat.query.filter_by(user_id=user_id, session_id=session_id).first()
    if not chat:
        chat = create_chat_instance(user_id, session_id)  
    return chat


def fetch_chat_history(user_id):
    chats = Chat.query.filter_by(user_id=user_id).all()
    chat_list = [chat.to_dict() for chat in chats]
    logger.info(f"Fetched chat history: {chat_list}") 
    return chat_list

def fetch_chat_messages(chat_id):
    """
    Fetches the messages for a specific chat ID as a plain Python structure.
    """
    chat = get_chat(chat_id)
    if not chat:
        return {"error": "Chat not found", "status": 404}
    
    sorted_messages = sorted(chat.messages, key=lambda m: m.timestamp)

    messages = [
        {
            "id": m.id,
            "sender": "User" if m.sender == "User" else "Brain", 
            "content": m.content,
            "edits": json.loads(m.edits) if m.edits else [],
            "edit_count": m.edit_count,
            "timestamp": m.timestamp
        }
        for m in sorted_messages
    ]
    return {"name": chat.name, "messages": messages, "status": 200}

def get_chat(chat_id):  
    if chat_id is None:
        return None 
    return Chat.query.get(chat_id)

def delete_chat_history(chat_id):
    try:
        chat = get_chat(chat_id)
        if chat is None:
            logger.error(f"Error: Chat with ID {chat_id} not found.")
            return {"error": "Chat not found", "status": 404}

        db.session.delete(chat)
        db.session.commit()

        logger.info(f"Chat deleted successfully. chat_id: {chat_id}")
        return {"message": "Chat deleted successfully", "status": 200}

    except IntegrityError as e:
        logger.exception(f"Database IntegrityError while deleting chat. chat_id: {chat_id}, error: {e}")
        return {"error": "Database integrity error", "status": 500}
    except OperationalError as e:
        logger.exception(f"Database OperationalError while deleting chat. chat_id: {chat_id}, error: {e}")
        return {"error": "Database operational error", "status": 500}
    except Exception as e:
        logger.exception(f"Unexpected error while deleting chat. chat_id: {chat_id}, error: {e}")
        return {"error": "An unexpected error occurred", "status": 500}


def edit_chat_history_name(new_chat_name, chat_id):
    if not new_chat_name:
        logger.error(f"Error: Attempt to update chat name with empty string. chat_id: {chat_id}")
        return {"error": "Chat name cannot be empty", "status": 400} 

    try:
        chat = get_chat(chat_id)
        if chat is None:
            logger.error(f"Error: Chat with ID {chat_id} not found.")
            return {"error": "Chat not found", "status": 404} 

        
        sanitized_name = sanitize_input(new_chat_name) 
        
        existing_chat = Chat.query.filter_by(name=sanitized_name).first()
        if existing_chat:
            return {"error": "Chat name already exists", "status": 400}

        chat.name = sanitized_name
        db.session.commit()
        
        logger.info(f"Chat name updated successfully. chat_id: {chat_id}, new_name: {sanitized_name}")
        return {"message": "Chat name updated successfully", "status": 200} 

    except IntegrityError as e:
        logger.exception(f"Database IntegrityError while updating chat name. chat_id: {chat_id}, error: {e}")
        return {"error": "Database integrity error", "status": 500} 
    except OperationalError as e:
        logger.exception(f"Database OperationalError while updating chat name. chat_id: {chat_id}, error: {e}")
        return {"error": "Database operational error", "status": 500} 
    except Exception as e:
        logger.exception(f"Unexpected error while updating chat name. chat_id: {chat_id}, error: {e}")
        return {"error": "An unexpected error occurred", "status": 500} 


def sanitize_input(input_string):
    """Sanitize input by allowing only alphanumeric characters, spaces, underscores, and hyphens."""
    return re.sub(r"[^a-zA-Z0-9 _-]", "", input_string)


def generate_chat_name(initial_prompt):
    """
    Generates a descriptive name for the chat based on the initial user prompt.
    """
    # Extract keywords from the initial prompt
    keywords = extract_keywords(initial_prompt)

    # Generate a base name using the first few keywords
    base_name = " ".join(keywords[:5])  # Limit to 3 keywords for brevity

    # Shorten and clean the name
    base_name = shorten_name(base_name)
    base_name = clean_name(base_name)

    return base_name


def extract_keywords(text):
    """
    Extracts keywords (nouns and verbs) from the given text.
    """
    try:
        tokens = word_tokenize(text.lower())
        pos_tags = pos_tag(tokens)
        keywords = [word for word, pos in pos_tags if pos in ['NN', 'NNS', 'VB', 'VBG', 'VBN', 'VBD']]
        return keywords
    except Exception as e:
        logger.error(f"Error extracting keywords: {e}", exc_info=True)
        return []


def shorten_name(name):
    """
    Shortens the name if it exceeds a certain length.
    """
    max_length = 30
    return name[:max_length] + "..." if len(name) > max_length else name


def clean_name(name):
    """
    Cleans the name by removing special characters and ensuring proper formatting.
    """
    return re.sub(r'[^\w\s-]', '', name).strip()
