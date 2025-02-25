from app.utils.ai_helper_methods import get_prompt, search_documents, fetch_document_content
import google.generativeai as gemini
from app.utils.config import config
from app.utils.logger import logger
from app.models.message import Message
from datetime import datetime
from app.models.database import db
from app.services.user_service import fetch_user_profile
from app.services.chat_service import get_or_create_default_chat, generate_chat_name, get_chat, fetch_chat_messages


gemini.configure(api_key=config.SECRET_KEY)


def send_message_receive_response(user_query, current_user, user_id, chat_id, session_id):
    """
    Processes the user's query and fetches the chat history, appending context to the AI prompt.
    """
    try:
        if current_user:
            user_profile = fetch_user_profile(user_id)
            user_role = user_profile.get("job_role")
            
            search_results = search_documents(user_query, user_id)
            logger.debug(f"Search results: {search_results}")

            document_context = search_results["content"]
        else:
            document_context = "Sorry, you have to be an authenticated user to access this data."

        # Use the updated fetch_chat_messages method
        chat_history_result = fetch_chat_messages(chat_id)
        if chat_history_result["status"] == 200:
            chat_history = chat_history_result["messages"]
        else:
            chat_history = []

        # Generate prompt with chat history
        prompt = get_prompt(document_context, user_query, user_role, chat_history)

        model = gemini.GenerativeModel("gemini-1.5-flash")
        chat_response = model.start_chat(history=[
            {"role": "user", "parts": prompt}
            
        ])

        answer = chat_response.send_message('text') 
        save_message(user_id, session_id, "User", user_query, chat_id)
        save_message(user_id, session_id, "Brain", answer.text, chat_id)

        return {"query": user_query, "answer": answer.text}

    except Exception as e:
        logger.error(f"Error in query_documents: {e}", exc_info=True)
        return {"error": f"Internal server error: {str(e)}"}




def save_message(user_id, session_id, sender, content, chat_id=None):
    try:
        if chat_id:
            chat = get_chat(chat_id)
            if not chat:
                raise ValueError(f"Chat with ID {chat_id} not found.")
        else:
            chat = get_or_create_default_chat(user_id, session_id)
        
        if not chat or not chat.id:
            raise ValueError("Failed to create or retrieve a valid chat instance.")
        
        if not chat.name and sender == 'User':
            chat.name = generate_chat_name(content)
            db.session.add(chat)
        
        message = Message(
            chat_id=chat.id,
            sender=sender,
            content=content,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        db.session.add(message)
        db.session.commit()
    except Exception as e:
        logger.error(f"Error saving query history: {e}", exc_info=True)
        raise
    