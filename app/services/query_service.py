from app.utils.ai_helper_methods import get_prompt, search_documents, fetch_user_role, fetch_document_content
import google.generativeai as gemini
from app.utils.config import config
from app.utils.logger import logger
from app.models.query_history import QueryHistory
from datetime import datetime
from app.models.database import db





gemini.configure(api_key=config.SECRET_KEY)


def query_documents(user_query, current_user, user_id, session_id):
    try:
        if current_user:
            user_role = fetch_user_role(user_id)
            
            search_results = search_documents(user_query)
            logger.debug(f"Search results: {search_results}")

            # document_ids = [result["id"] for result in search_results]
            document_ids = search_results["ids"]
            document_context = fetch_document_content(document_ids, user_id)
        else:
            document_context = "Sorry you have to be an authenticated user to access this data."
            
        prompt = get_prompt(document_context, user_query, user_role)

        model = gemini.GenerativeModel("gemini-1.5-pro")
       
        chat_response = model.start_chat(history=[
            {"role": "user", "parts": prompt}
        ])

        answer = chat_response.send_message('text') 
        save_query_history(user_id, user_query, answer.text, session_id)

        return {"query": user_query, "answer": answer.text}
    
    except Exception as e:
        logger.error(f"Error in query_documents: {e}", exc_info=True)
        return {"error": f"Internal server error: {str(e)}"} 


def save_query_history(user_id, query_text, response_text, session_id):
    try:
        query_history = QueryHistory(
            user_id=user_id,
            query_text=query_text,
            response_text=response_text,
            session_id=session_id,
            created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        db.session.add(query_history)
        db.session.commit()
        return query_history
    except Exception as e:
        logger.error(f"Error saving query history: {e}", exc_info=True)
        raise
    
def fetch_user_query_history(user_id, topic=None):
    try:
        query = QueryHistory.query.filter_by(user_id=user_id)
        if topic:
            query = query.filter(QueryHistory.query_text.ilike(f'%{topic}%'))
        query_history = query.order_by(QueryHistory.created_at.desc()).all()
        return [query.to_dict() for query in query_history]
    except Exception as e:
        logger.error(f"Error fetching query history: {e}", exc_info=True)
        return {"error": str(e)}